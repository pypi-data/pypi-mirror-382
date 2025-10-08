from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from ....system.color_manipulator import alpha
from .properties_name import *

class RadioStyle:
    MuiFormControlLabel: str = "" 
    MuiRadio: str = "" 



def rating(_theme) -> Dict:
    theme: ThemeState = _theme
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'

    return {
        'PyRating': {
            'styles': {
                'root': {
                    "color": theme.palette.warning.main,
                    "slots": {
                        "disabled": {
                            opacity: 0.48
                        },
                    },
                    "props": {
                        "iconEmpty": {
                            color: alpha(theme.palette.grey._500, 0.48),
                        },
                        "sizeSmall": {
                            "svgIcon": {
                                width: 20,
                                height: 20,
                            }
                        },
                        "sizeMedium": {
                            "svgIcon": {
                                width: 24,
                                height: 24,
                            }
                        },
                        "sizeLarge": {
                            "svgIcon": {
                                width: 28,
                                height: 28,
                            }
                        },
                    }
                },
                "icon": {
                    "root": {
                        "color": theme.palette.grey._500,
                        "slots": {
                            "selected": {
                                "color": theme.palette.warning.main
                            }
                        }
                    }
                }
            }
        },

    }
