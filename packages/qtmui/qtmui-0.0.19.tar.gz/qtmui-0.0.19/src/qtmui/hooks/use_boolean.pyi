from qtmui.hooks.use_state import useState, State
from dataclasses import dataclass
from typing import Callable, Dict
from qtpy.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QWidget, QLineEdit
from qtpy.QtCore import QObject, Property, Signal
class ReturnType:
    state: State
    onTrue: Callable
    onFalse: Callable
    onToggle: Callable
    toggle: Callable
class UseBoolean:
    def __init__(self, initValue): ...
    def onTrue(self, *args, **kwargs): ...
    def onFalse(self): ...
    def onToggle(self): ...
def useBoolean(initValue): ...