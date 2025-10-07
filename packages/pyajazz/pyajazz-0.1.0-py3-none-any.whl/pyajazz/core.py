from functools import partial
import time
from typing import Optional, Callable
import queue
import hid
import threading
import logging

from .protocol import (
    IMAGE_CHUNK_SIZE,
    BUTTON_IMAGE_MAX_SIZE,
    LOGO_IMAGE_MAX_SIZE,
    INPUT_REQUEST_PREFIX,
    INPUT_REQUEST_ACTION_TYPE_MAPPING,
    DeviceCommand,
    InputRequestLayout,
    BacklightRequestLayout,
    ClearButtonRequestLayout,
    ImgAnnounceRequestLayout,
    LogoAnnounceRequestLayout,
    DeviceState,
)

from .inputs import Button, InputAction


_logger = logging.getLogger(__name__)


class Device:
    def __init__(
            self,
            vendor_id=0x0300,
            product_id=0x3010,
            buttons: Optional[list[int]] = None,
            append_zero_byte: bool = True,
            keepalive_interval: int = 5
    ) -> None:
        """
        Initializes a new Device instance.

        :param vendor_id: USB vendor ID of the target device.
        :type vendor_id: int
        :param product_id: USB product ID of the target device.
        :type product_id: int
        :param buttons: List of IDs at which buttons will be initialized,
            if None standard AKP153 setup is done (1 to 15).
        :type buttons: Optional[list[int]]
        :param append_zero_byte: A flag to prepend 0x00 byte to each HID request sent
        :type append_zero_byte: bool, default: True
        :param keepalive_interval: Interval at which keep-alive requests are sent
        :type keepalive_interval: int, default: 5
        """

        self._keepalive_interval = keepalive_interval
        self._append_zero_byte = append_zero_byte

        self.state_lock = threading.Lock()
        with self.state_lock:
            self.state = DeviceState.NOT_CONNECTED
        self.error_msg = ""

        self._writer_running = threading.Event()
        self._listener_running = threading.Event()

        self.device_vid = vendor_id
        self.device_pid = product_id
        self._device = hid.device()

        self._writer_thread: Optional[threading.Thread] = None
        self._listener_thread: Optional[threading.Thread] = None

        self._writer_queue: queue.Queue[bytes] = queue.Queue()
        self._listener_queue: queue.Queue[bytes] = queue.Queue()

        if buttons is None:
            buttons = range(1, 16)

        self._inputs = {
            button_id: Button(
                set_image_callback=partial(self.set_button_image, position=button_id),
                clear_image_callback=partial(self.clear_button_image, position=button_id)
                )
            for button_id in buttons
        }

    def __enter__(self) -> "Device":
        """
        Enters a context-managed block, starting the device connection.

        :return: The device instance.
        :rtype: Device
        """

        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()

    def _listener_loop(self):
        while self._listener_running.is_set():
            try:
                data = self._device.read(1024, timeout_ms=100)
                if data:
                    self._listener_queue.put(bytes(data))
            except Exception as e:
                threading.Thread(
                        target=self.stop,
                        kwargs={"error_msg": f"Read failed! ({type(e).__name__}: {e})"},
                        daemon=False
                ).start()
                break
        
    def _writer_loop(self):
        while self._writer_running.is_set() or not self._writer_queue.empty():
            try:
                data = self._writer_queue.get(timeout=self._keepalive_interval)
                self._device.write(data)
                self._writer_queue.task_done()
            except queue.Empty:
                self.write(DeviceCommand.KEEPALIVE.value)
            except Exception as e:
                threading.Thread(
                    target=self.stop,
                    kwargs={"error_msg": f"Write failed! ({type(e).__name__}: {e})"},
                    daemon=False
                ).start()
                break

    def _handle_request(self, data: bytes):
        if data.startswith(INPUT_REQUEST_PREFIX):
            input_id = data[InputRequestLayout.INPUT_ID]
            action_type = INPUT_REQUEST_ACTION_TYPE_MAPPING.get(data[InputRequestLayout.ACTION])
            if action_type is None:
                _logger.warning(f"Unknown input request (Unhandled action type value: 0x{data[InputRequestLayout.ACTION]:02x}): {data}")
                return

            if input_id in self._inputs:
                self._inputs[input_id].handle_action(action_type)
                _logger.info(f">> Handling action: input_id:{input_id}, action_type:{action_type}")
            else:
                _logger.warning(f"Unknown input request (Unhandled input id: 0x{input_id:02x}): {data}")
        else:
            _logger.warning(f"Unknown input request: {data}")

    def _set_input_callback(self, input_id, action_type: InputAction, callback: Callable | None):
        if input_id not in self._inputs:
            raise ValueError(f"Invalid input ID: {input_id}")
     
        self._inputs[input_id].set_callback(action_type=action_type, callback=callback)   

    def write(self, data: bytes | bytearray | list[int]):
        """
        Queues a message to be written to the device.

        :param data: The data to send.
        :type data: bytes | bytearray | list[int]
        :raises ValueError: If device is not connected.
        :raises TypeError: If data is of unsupported type.
        """

        if not self.connected:
            raise ValueError(f"Can't write to device - device status: {self.get_state()}")

        if not isinstance(data, bytes):
            if isinstance(data, (bytearray, list)):
                data = bytes(data)
            else:
                raise TypeError(f"Unsupported data type: {type(data).__name__}")
        
        if self._append_zero_byte:
            data = b'\x00' + data
        self._writer_queue.put(data)

    def handle_pending_inputs(self):
        """
        Handles all pending input requests from the listener queue.
        """

        while not self._listener_queue.empty():
            message = self._listener_queue.get_nowait()
            self._handle_request(message)
            self._listener_queue.task_done()

    def get_state(self) -> DeviceState:
        """
        Gets the current state of the device.

        :return: The device state.
        :rtype: DeviceState
        """

        with self.state_lock:
            return self.state
        
    def get_error_msg(self) -> str:
        """
        Gets the last error message. Returns empty string on no error.

        :return: The error message.
        :rtype: str
        """

        with self.state_lock:
            return self.error_msg
        
    @property
    def connected(self) -> bool:
        """
        Indicates whether the device is currently connected.

        :return: True if connected, False otherwise.
        :rtype: bool
        """

        return self.get_state() == DeviceState.CONNECTED

    def start(self):
        """
        Starts the device connection, initializing threads and communication.
        
        :raises OSError: If the device cannot be opened.
        """

        if self.connected:
            _logger.warning("'start()' method called while already connected")
            return
        try:
            self._writer_queue = queue.Queue()
            self._listener_queue = queue.Queue()

            self._device.open(self.device_vid, self.device_pid)
            self._device.set_nonblocking(True)

            self._writer_running.set()
            self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self._writer_thread.start()

            with self.state_lock:
                self.state = DeviceState.CONNECTED
                self.error_msg = ""

            self.write(DeviceCommand.INIT.value)
            self.write(DeviceCommand.CLEAR_ALL.value)
            self.write(DeviceCommand.FLUSH_BUFFER.value)

            self._listener_running.set()
            self._listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
            self._listener_thread.start()

        except Exception as e:  
            with self.state_lock:
                self.state = DeviceState.NOT_CONNECTED
            raise OSError(f"Can't connect to device (VID: 0x{self.device_vid:04x}, PID: 0x{self.device_pid:04x})") from e
        

    def stop(self, error_msg: Optional[str] = None):
        """
        Stops the device, terminating threads and closing the connection.

        :param error_msg: Optional error message to set the device to ERROR state.
        :type error_msg: str or None
        """

        if not self.connected:
            _logger.warning("'stop()' method called while already disconnected")
            return

        self._listener_running.clear()
        if self._listener_thread is not None and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=15)
        
        self.write(DeviceCommand.CLEAR_ALL_SHOW_LOGO.value)

        self._writer_running.clear()
        if self._writer_thread is not None and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=15)

        self._device.close()

        with self.state_lock:
            if error_msg:
                self.state = DeviceState.ERROR
                self.error_msg = f"Connection dropped on error: {error_msg}"
            else: 
                self.state = DeviceState.NOT_CONNECTED

    def set_brightness(self, brightness: int):
        """
        Sets the backlight brightness of the device.

        :param brightness: Brightness level (0-100).
        :type brightness: int
        :raises ValueError: If brightness is out of bounds.
        """
        
        if brightness<0 or brightness>100:
            raise ValueError("Incorrect brightness!")
        packet = bytearray(DeviceCommand.BACKLIGHT_BRIGHTNESS.value)
        packet[BacklightRequestLayout.BRIGHTNESS] = brightness
        self.write(packet)

    def _send_image_data(self, data: bytes | bytearray | list[int]):
        for start in range(0, len(data), IMAGE_CHUNK_SIZE):
            self.write(data[start:start+IMAGE_CHUNK_SIZE])

    def set_button_image(self, position: int, data: bytes | bytearray | list[int]):
        """
        Sets an image on the specified button.

        :param position: The ID of the button to set image.
        :type position: int
        :param data: Image data to display.
        :type data: bytes | bytearray | list[int]
        :raises ValueError: If image data is invalid or too large.
        """
        
        if not isinstance(data, (bytes, bytearray, list)) or len(data) == 0:
            raise ValueError("Invalid image data")
        
        img_size = len(data)
        if img_size > BUTTON_IMAGE_MAX_SIZE:
            raise ValueError(f"Image size too big - got: {img_size}, max allowed: {BUTTON_IMAGE_MAX_SIZE}")

        packet = bytearray(DeviceCommand.IMG_ANNOUNCE.value)
        packet[ImgAnnounceRequestLayout.SIZE_1] = img_size // 256
        packet[ImgAnnounceRequestLayout.SIZE_0] = img_size % 256
        packet[ImgAnnounceRequestLayout.POSITION] = position
        
        self.write(packet)
        self._send_image_data(data)
        self.write(DeviceCommand.FLUSH_BUFFER.value)

    def clear_button_image(self, position: int):
        """
        Clears the image from the specified button.

        :param position: The ID of the button to clear.
        :type position: int
        """
        
        packet = bytearray(DeviceCommand.CLEAR_BUTTON.value)
        packet[ClearButtonRequestLayout.POSITION] = position
        self.write(packet)
        self.write(DeviceCommand.FLUSH_BUFFER.value)

    def clear_all(self):
        """
        Clears the whole screen of the device.
        """
        self.write(DeviceCommand.CLEAR_ALL.value)
        self.write(DeviceCommand.FLUSH_BUFFER.value)

    def sleep(self):
        """
        Turns off the screen while allowing to receive commands. Please note that while asleep
        the first input event does not trigger any HID request, since it is used by the device 
        internally to wake it up.
        in such circumstances. 
        """
        self.write(DeviceCommand.SLEEP.value)

    def wakeup(self):
        """
        Wakes up the device from sleep mode.
        """
        self.write(DeviceCommand.INIT.value)

    def set_logo_image(self, data: bytes | bytearray | list[int]):
        """
        Sets the logo image to be displayed on the device while not connected.

        :param data: Logo image data.
        :type data: bytes | bytearray | list[int]
        :raises ValueError: If image data is invalid or too large.
        """
        if not isinstance(data, (bytes, bytearray, list)) or len(data) == 0:
            raise ValueError("Invalid image data")

        img_size = len(data)
        if img_size > LOGO_IMAGE_MAX_SIZE:
            raise ValueError(f"Image size too big - got: {img_size}, max allowed: {LOGO_IMAGE_MAX_SIZE}")

        packet = bytearray(DeviceCommand.LOGO_ANNOUNCE.value)
        packet[LogoAnnounceRequestLayout.SIZE_2] = img_size // 256**2
        packet[LogoAnnounceRequestLayout.SIZE_1] = img_size // 256 % 256
        packet[LogoAnnounceRequestLayout.SIZE_0] = img_size % 256

        self.write(packet)
        self._send_image_data(data)
        self.write(DeviceCommand.FLUSH_BUFFER.value)
        time.sleep(1) # Give some time to process and show the logo
        self.write(DeviceCommand.CLEAR_ALL.value)
        self.write(DeviceCommand.FLUSH_BUFFER.value)

    def on_press(self, position: int, callback: Callable):
        """
        Configures button press callback.

        :param position: The ID of the button.
        :type position: int
        :param callback: Function to call on button press event.
        :type callback: Callable
        """
        self._set_input_callback(input_id=position, action_type=InputAction.PRESS, callback=callback)

    def on_release(self, position: int, callback: Callable):
        """
        Configures button release callback.

        :param position: The ID of the button.
        :type position: int
        :param callback: Function to call on button release event.
        :type callback: Callable
        """
        self._set_input_callback(input_id=position, action_type=InputAction.RELEASE, callback=callback)

    def clear_callbacks(self, position: Optional[int] = None):
        """
        Removes all button event callbacks for given button/all buttons (`position` set to None).

        :param position: The ID of the button. If none clears callback of all buttons.
        :type position: int
        """
        if position is None:
            for position in self._inputs:
                self._set_input_callback(input_id=position, action_type=InputAction.PRESS, callback=None)
                self._set_input_callback(input_id=position, action_type=InputAction.RELEASE, callback=None)
        else:
            self._set_input_callback(input_id=position, action_type=InputAction.PRESS, callback=None)
            self._set_input_callback(input_id=position, action_type=InputAction.RELEASE, callback=None)
        
