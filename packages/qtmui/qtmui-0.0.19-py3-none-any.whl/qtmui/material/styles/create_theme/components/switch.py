from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from ....system.color_manipulator import alpha
from .properties_name import *

def switch(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == 'light'
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    return {
        'PySwitch': {
            'styles': {
                'root': {
                    **{
                        "default": {
                            'indicatorColorChecked': theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            'barColor': theme.palette.grey._500,
                            'handleColor': theme.palette.common.white if lightMode else theme.palette.grey._800,
                            'pulseCheckedColor': theme.palette.grey._700 if lightMode else theme.palette.grey._400,
                            'pulseUncheckedColor': theme.palette.common.white if lightMode else theme.palette.grey._800,
                            'checkedColor': theme.palette.grey._800 if lightMode else theme.palette.common.white
                        },
                        "inherit": {
                            'indicatorColorChecked': theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            'barColor': theme.palette.grey._500,
                            'handleColor': theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            'pulseCheckedColor': theme.palette.grey._700 if lightMode else theme.palette.grey._400,
                            'pulseUncheckedColor': theme.palette.common.white if lightMode else theme.palette.grey._800,
                            'checkedColor': theme.palette.grey._800 if lightMode else theme.palette.common.white
                        }
                    },
                    **{
                        f"{_color}": {
                            'indicatorColorChecked': getattr(theme.palette, _color).main,
                            'barColor': theme.palette.grey._500,
                            'handleColor': theme.palette.common.white,
                            'pulseCheckedColor': getattr(theme.palette, _color).light if lightMode else getattr(theme.palette, _color).dark,
                            'pulseUncheckedColor': getattr(theme.palette, _color).main,
                            'checkedColor': getattr(theme.palette, _color).main,
                        }
                        for _color in COLORS
                    }
                }
            }
        },
    }
