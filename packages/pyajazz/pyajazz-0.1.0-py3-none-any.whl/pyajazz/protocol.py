from dataclasses import dataclass
import enum


IMAGE_CHUNK_SIZE = 1024
BUTTON_IMAGE_MAX_SIZE = 1024*10
LOGO_IMAGE_MAX_SIZE = 1024*512

INPUT_REQUEST_PREFIX = bytes([0x41, 0x43, 0x4b, 0x00, 0x00, 0x4f, 0x4b, 0x00, 0x00])
OUTPUT_REQUEST_PREFIX = bytes([0x43, 0x52, 0x54, 0x00, 0x00])

@dataclass(frozen=True)
class InputRequestLayout:
    INPUT_ID: int = 9
    ACTION: int = 10


@dataclass(frozen=True)
class BacklightRequestLayout:
    BRIGHTNESS: int = 10


@dataclass(frozen=True)
class ClearButtonRequestLayout:
    POSITION: int = 11


@dataclass(frozen=True)
class ImgAnnounceRequestLayout:
    SIZE_1: int = 10
    SIZE_0: int = 11
    POSITION: int = 12


@dataclass(frozen=True)
class LogoAnnounceRequestLayout:
    SIZE_2: int = 9
    SIZE_1: int = 10
    SIZE_0: int = 11


def output_request_command(command_suffix: list[int]) -> bytes:
    return OUTPUT_REQUEST_PREFIX + bytes(command_suffix)


class DeviceCommand(enum.Enum):
    INIT = output_request_command([0x44, 0x49, 0x53])
    KEEPALIVE = output_request_command([0x43, 0x4f, 0x4e, 0x4e, 0x45, 0x43, 0x54])
    FLUSH_BUFFER = output_request_command([0x53, 0x54, 0x50])
    BACKLIGHT_BRIGHTNESS = output_request_command([0x4c, 0x49, 0x47, 0x00, 0x00, 0x32])
    SLEEP = output_request_command([0x48, 0x41, 0x4e])
    CLEAR_BUTTON = output_request_command([0x43, 0x4c, 0x45, 0x00, 0x00, 0x00, 0x00])
    CLEAR_ALL = output_request_command([0x43, 0x4c, 0x45, 0x00, 0x00, 0x00, 0xff])
    CLEAR_ALL_SHOW_LOGO =  output_request_command([0x43, 0x4c, 0x45, 0x00, 0x00, 0x44, 0x43])
    IMG_ANNOUNCE = output_request_command([0x42, 0x41, 0x54, 0x00, 0x00, 0x00, 0x00, 0x00])
    LOGO_ANNOUNCE = output_request_command([0x4c, 0x4f, 0x47, 0x00, 0x00, 0x00, 0x00, 0x01])


class InputAction(enum.Enum):
    PRESS = "press"
    RELEASE = "release"


class DeviceState(enum.Enum):
    NOT_CONNECTED = enum.auto()
    CONNECTED = enum.auto()
    ERROR = enum.auto()


INPUT_REQUEST_ACTION_TYPE_MAPPING = {
    0x00: InputAction.RELEASE,
    0x01: InputAction.PRESS
}