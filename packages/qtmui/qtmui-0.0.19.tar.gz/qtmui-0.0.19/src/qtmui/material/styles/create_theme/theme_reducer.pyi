from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any, Callable, Union
import threading
from immutable import Immutable
import uuid
from dataclasses import field, replace
from redux import ReducerResult, CompleteReducerResult, BaseAction, BaseEvent, Store
from typing import Callable, Sequence, Optional
from qtpy.QtCore import QPoint, QSize
from qtpy.QtGui import QColor
from .shape import ShapeOptions, Shape
from .create_breakpoints import BreakpointsOptions, Breakpoints
from .create_spacing import SpacingOptions, Spacing, create_spacing
from ..style_function_sx.style_function_sx import SxProps
from ..style_function_sx.default_sx_config import SxConfig
from .apply_styles import ApplyStyles
from .typography import Typography
from .palette import palette
from .create_palette import create_palette, Palette
from .create_size import create_size, Sizes
from .create_shadows import create_shadows, Shadows
from .create_root_component_styles import create_root_component_styles
class Direction:
class ThemeOptions:
    shape: Optional[ShapeOptions]
    breakpoints: Optional[BreakpointsOptions]
    direction: Optional[Direction]
    mixins: Optional[Any]
    palette: Optional[Dict[str, Any]]
    customShadows: Optional[Shadows]
    spacing: Optional[SpacingOptions]
    transitions: Optional[Any]
    components: Optional[Dict[str, Any]]
    typography: Optional[Any]
    zIndex: Optional[Dict[str, int]]
    unstable_sxConfig: Optional[SxConfig]
    size: Optional[Dict[str, Any]]
class Context:
    mainwindow_pos: Optional[ShapeOptions]
    mainwindow_size: Optional[ShapeOptions]
class Changed:
    connect: Optional[object]
class Signal:
    changed: Optional[Changed]
class ThemeState:
    signal: Optional[Signal]
    context: Context
    shape: Shape
    breakpoints: Breakpoints
    direction: Direction
    palette: Palette
    customShadows: Optional[Shadows]
    spacing: Spacing
    transitions: Optional[Any]
    components: Optional[Dict[str, Any]]
    mixins: Optional[Any]
    typography: Typography
    zIndex: Optional[Dict[str, int]]
    applyStyles: Optional[Callable[Any, ApplyStyles]]
    unstable_sxConfig: Optional[SxConfig]
    unstable_sx: Optional[Callable[Any, Dict[str, Any]]]
    size: Optional[Sizes]
class CreateThemeAction:
class ChangePaletteAction:
    mode: Literal[Any, Any]
class MergeOverideComponentsAction:
    components: Dict
class UpdateMainwindowPositionAction:
    mainWindowPosition: QPoint
def createTheme(options: Optional[ThemeOptions], *args): ...
def theme_reducer(state: Any, action: BaseAction): ...