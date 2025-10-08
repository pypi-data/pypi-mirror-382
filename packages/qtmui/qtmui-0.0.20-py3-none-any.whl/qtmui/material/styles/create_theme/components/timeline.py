from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def timeline(_theme) -> Dict:
    theme: ThemeState = _theme

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    lightMode = theme.palette.mode == "light"

    return {
        "PyTimeLine": {
            "styles": {
                
                "dot": {
                    **{
                        "default": {
                            color: theme.palette.grey._800 if lightMode else theme.palette.common.white
                        },
                        "inherit": {
                            color: theme.palette.grey._700 if lightMode else theme.palette.grey._100
                        }
                    },
                    **{
                        _color: {
                            color: getattr(theme.palette, _color).main,
                        }
                        for _color in COLORS
                    }
                },
                "connector": {
                    **{
                        "default": {
                            color: theme.palette.grey._800 if lightMode else theme.palette.common.white
                        },
                        "inherit": {
                            color: theme.palette.grey._700 if lightMode else theme.palette.grey._100
                        }
                    },
                    **{
                        _color: {
                            color: getattr(theme.palette, _color).main,
                        }
                        for _color in COLORS
                    }
                },
            }
        },

    }
