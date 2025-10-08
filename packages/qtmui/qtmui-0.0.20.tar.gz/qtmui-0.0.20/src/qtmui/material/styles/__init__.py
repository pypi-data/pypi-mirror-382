from dataclasses import field, replace
from functools import lru_cache

from redux.main import Store

from ...material.styles.create_theme.theme_reducer import CreateThemeAction, ChangePaletteAction, ThemeState

from .root_reducer import root_reducer, StateType, ActionType


from qtpy.QtCore import QObject, Property, Signal

from ..system import (
    hexToRgb,
    rgbToHex,
    hslToRgb,
    decomposeColor,
    recomposeColor,
    getContrastRatio,
    getLuminance,
    emphasize,
    alpha,
    darken,
    lighten,
)

from .styled import styled

class ThemeSignal(QObject):
    changed = Signal()

    def __init__(self, theme=None):
        super().__init__()
        self._theme = theme

    def getTheme(self) -> dict:
        return self._theme

    def setTheme(self, value):
        if self._theme != value:
            self._theme = value
            self.changed.emit()

    theme = Property(str, getTheme, setTheme, notify=changed)

themeSignal = ThemeSignal()

def onThemeChanged(data: dict):
    themeSignal.theme = data
    

store: Store[StateType, ActionType, None] = Store(root_reducer)
store.dispatch(CreateThemeAction())


def setTheme(mode):
    store.dispatch(ChangePaletteAction(mode=mode))
    onThemeChanged(store._state.theme)

# @lru_cache(maxsize=128) ===> lỗi 

def useTheme():
    theme: ThemeState = store._state.theme
    theme = replace(theme, signal=themeSignal)
    return theme



