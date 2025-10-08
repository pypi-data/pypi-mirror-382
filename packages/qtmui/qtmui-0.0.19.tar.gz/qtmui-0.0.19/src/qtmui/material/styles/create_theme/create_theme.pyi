from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, Union
from .shape import ShapeOptions, Shape
from .create_breakpoints import BreakpointsOptions, Breakpoints
from .create_spacing import SpacingOptions, Spacing
from ..style_function_sx.style_function_sx import SxProps
from ..style_function_sx.default_sx_config import SxConfig
from .apply_styles import ApplyStyles
class Direction:
class ThemeOptions:
    shape: Optional[ShapeOptions]
    breakpoints: Optional[BreakpointsOptions]
    direction: Optional[Direction]
    mixins: Optional[Any]
    palette: Optional[Dict[str, Any]]
    shadows: Optional[Any]
    spacing: Optional[SpacingOptions]
    transitions: Optional[Any]
    components: Optional[Dict[str, Any]]
    typography: Optional[Any]
    zIndex: Optional[Dict[str, int]]
    unstable_sxConfig: Optional[SxConfig]
class Theme:
    shape: Shape
    breakpoints: Breakpoints
    direction: Direction
    palette: Dict[str, Any]
    shadows: Optional[Any]
    spacing: Spacing
    transitions: Optional[Any]
    components: Optional[Dict[str, Any]]
    mixins: Optional[Any]
    typography: Optional[Any]
    zIndex: Optional[Dict[str, int]]
    applyStyles: Optional[Callable[Any, ApplyStyles]]
    unstable_sxConfig: Optional[SxConfig]
    unstable_sx: Optional[Callable[Any, Dict[str, Any]]]
def createTheme(options: Optional[ThemeOptions], *args): ...