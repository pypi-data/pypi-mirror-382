from qtpy.QtWidgets import QFrame, QVBoxLayout, QApplication
from qtpy.QtCore import QSize
from ..alert.alert import Alert
from ..button import Button
from ..py_tool_button.py_tool_button import Iconify
from ..snackbar import Snackbar
from ..box import Box
from ..stack import QStack
from ..typography import Typography
class IconBox:
    def __init__(self, context, path: str): ...
    def _copy_to_clipboard(self, icon_p): ...
    def _create_snackbar(self, message): ...