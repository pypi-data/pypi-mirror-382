from typing import Callable, Optional, Union
import uuid
from qtpy.QtCore import Qt, Property, Slot, Signal
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qtmui.hooks.use_state import State
from ...material.masonry.masonry import Masonry
from qtmui.hooks import useState
from ..controller import Controller
from ..form_control_label import FormControlLabel
from ..box import Box
from ..form_control import FormControl
from ..form_label import FormLabel
from ..radio import Radio
from ..radio_group import RadioGroup
from qtmui.material.styles import store, useTheme
from ..qss_name import *
class RHFRadioGroup:
    def __init__(self, name: str, key: Optional[str], value: object, orientation: str, label: Optional[Union[str, State, Callable]], options: object, spacing: int, helperText: str, row: bool): ...
    def _init_ui(self): ...
    def set_value(self, value): ...
    def _on_change(self, value): ...
    def stateSignal(self): ...
    def stateSignal(self, value): ...
    def state(self, state): ...