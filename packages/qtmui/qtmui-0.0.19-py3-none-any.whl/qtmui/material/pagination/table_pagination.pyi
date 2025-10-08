import uuid
from qtpy.QtWidgets import QWidget, QHBoxLayout, QFrame
from qtpy.QtCore import Qt, Signal
from typing import Callable, Optional, Union
from qtmui.hooks.use_state import State
from qtmui.hooks import useEffect, useState
from ..stack import Stack
from ..typography import Typography
from ..button import IconButton
from ..select import Select
from ..py_iconify import Iconify
from ..textfield import TextField
from ..menu_item import MenuItem
from src.locales.translator import Translator
class TablePagination:
    def __init__(self, count: State, page: State, onPageChange: Callable[Any, Any], rowsPerPage: State, onRowsPerPageChange: Callable[Any, Any], children: Optional[Union[list, QWidget]], rowsPerPageOptions: Optional[Union[list, QWidget]]): ...