from dataclasses import dataclass, field
from typing import Callable, Optional, Union, Dict
from ....material.system.color_manipulator import get_contrast_text
class CommonColors:
    black: str
    white: str
class Color:
    _50: str
    _100: str
    _200: str
    _300: str
    _400: str
    _500: str
    _600: str
    _700: str
    _800: str
    _900: str
class PaletteColor:
    light: Optional[str]
    lighter: Optional[str]
    main: str
    dark: Optional[str]
    darker: Optional[str]
    contrastText: Optional[str]
class TypeText:
    primary: str
    secondary: str
    disabled: str
class TypeAction:
    active: str
    hover: str
    hoverOpacity: float
    selected: str
    selectedOpacity: float
    disabled: str
    disabledBackground: str
    disabledOpacity: float
    focus: str
    focusOpacity: float
    activatedOpacity: float
class TypeBackground:
    default: str
    paper: str
    notched: str
    neutral: str
    navigation: str
    main: str
    second: str
    thirty: str
    content: str
    transparent: str
class Palette:
    common: CommonColors
    mode: str
    contrastThreshold: float
    tonalOffset: Union[float, Dict[str, float]]
    primary: PaletteColor
    secondary: PaletteColor
    error: PaletteColor
    warning: PaletteColor
    info: PaletteColor
    success: PaletteColor
    grey: Color
    text: TypeText
    divider: str
    action: TypeAction
    background: TypeBackground
    getContrastText: Callable[Any, str]
    augmentColor: Callable[Any, PaletteColor]
def get_default_primary(mode: str): ...
def get_default_secondary(mode: str): ...
def get_default_error(mode: str): ...
def augment_color(options: Dict): ...
def augment_text_color(options: Dict): ...
def create_palette(palette: Dict): ...