import uuid
from qtpy.QtWidgets import QHBoxLayout, QFrame
class ToolBar:
    def __init__(self, variant: str, disableGutters: bool, sx: dict, children: list, height: int, *args, **kwargs): ...