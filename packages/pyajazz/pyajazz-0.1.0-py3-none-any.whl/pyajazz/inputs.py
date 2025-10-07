import logging
from typing import Callable, Optional

from .protocol import (
    InputAction
)


_logger = logging.getLogger(__name__)


class PhysicalInput:
    input_id: Optional[int]
    on_action: dict[InputAction, Callable]

    def __init__(self, input_id: Optional[int] = None):
        self.input_id = input_id
        self.on_action = {}

    def handle_action(self, action_type: InputAction):
        if action_type in self.on_action:
            self.on_action[action_type]()

    def set_callback(self, action_type: InputAction, callback: Callable | None):
        if callback is None:
            self.on_action.pop(action_type, None)
        elif callable(callback):
            self.on_action[action_type] = callback
        else:
            raise ValueError("Improper callback provided")

class Button(PhysicalInput):
    set_image_callback: Optional[Callable]
    clear_image_callback: Optional[Callable]

    def __init__(
        self,
        input_id: Optional[int] = None,
        set_image_callback: Optional[Callable] = None,
        clear_image_callback: Optional[Callable] = None
    ):
        super().__init__(input_id=input_id)

        self.set_image_callback = set_image_callback
        self.clear_image_callback = clear_image_callback

    def set_image(self, data: bytes | bytearray | list[int]):
        if self.set_image_callback is not None:
            self.set_image_callback(data=data)
        else:
            _logger.warning("No set_image_callback set!")

    def clear_image(self):
        if self.clear_image_callback is not None:
            self.clear_image_callback()
        else:
            _logger.warning("No clear_image_callback set!")