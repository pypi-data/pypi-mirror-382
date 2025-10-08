from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def py_tool_button(_theme) -> Dict:
    theme: ThemeState = _theme

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'

    return {
        'PyToolButton': {
            'styles': {
                'root':  {
                    **{
                        "default": {
                            backgroundColor: "transparent",
                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                            "slots": {
                                "hover": {
                                    color: theme.palette.action.hover,
                                }
                            },
                        },
                    },
                    **{
                        f"{_color}": {
                            backgroundColor: "transparent",
                            color: getattr(theme.palette, _color).main,
                            "slots": {
                                "hover": {
                                    color: alpha(getattr(theme.palette, _color).main, 0.08),
                                },
                            },
                        }
                        for _color in COLORS
                    }
                }
            }
        },
        'PyToolButtonSize': {
            'styles': {
                'small': {
                    height: '20px',
                    borderRadius: "10px"
                },
                'medium': {
                    height: '24px',
                    borderRadius: "12px"
                },
            }
        }
    }
