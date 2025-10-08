from qtpy.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel
from qtpy.QtCore import Qt
from typing import TYPE_CHECKING, Union
from .treeview_model import TreeViewModel
class TreeView:
    def __init__(self, model: Union[TreeViewModel], rootIndexPath: str): ...