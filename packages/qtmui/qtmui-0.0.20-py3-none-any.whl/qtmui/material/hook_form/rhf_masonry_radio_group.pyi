from typing import Callable, Optional, Union
import uuid
from qtpy.QtWidgets import QWidget, QVBoxLayout
from qtmui.hooks.use_state import State
from ...material.masonry.masonry import Masonry
from ..controller import Controller
from ..form_control_label import FormControlLabel
from ..box import Box
from ..form_control import FormControl
from ..form_label import FormLabel
from ..radio import Radio
from ..radio_group import RadioGroup
from ..qss_name import *
class RHFMasonryRadioGroup:
    def __init__(self, name, id: str, value: object, row: str, columns: int, checked: bool, isVisible: bool, label: Optional[Union[str, State, Callable]], options: object, spacing: int, minWidth: int, helperText: str, color: str, isOptionEqualToValue: Optional[Callable]): ...
    def setup_ui(self): ...
    def renderRadioGroup(self): ...
    def _set_hide(self, state): ...
    def _set_visible(self, state): ...
    def set_value(self, value): ...