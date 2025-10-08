from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from ....system.color_manipulator import alpha
from .properties_name import *

class RadioStyle:
    MuiFormControlLabel: str = "" 
    MuiRadio: str = "" 



def radio(_theme) -> Dict:
    theme: ThemeState = _theme
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'

    return {
        # CHECKBOX, RADIO, SWITCH
        'PyFormControlLabel': {
            'styles': {
                'label': {
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: theme.typography.body2.fontWeight,
                    lineHeight: theme.typography.body2.lineHeight,
                }
            },
        },

        'PyRadio': {
            'styles': {
                'root': {
                    **{
                        "default": {
                            color: theme.palette.grey._900 if lightMode else theme.palette.common.white,
                            p: theme.spacing,
                        },
                        "inherit": {
                            color: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            p: theme.spacing,
                        }
                    },
                    **{
                        f"{_color}": {
                            color: getattr(theme.palette, _color).main,
                            p: theme.spacing,
                        }
                        for _color in COLORS
                    }
                }
            }
        },

    }
