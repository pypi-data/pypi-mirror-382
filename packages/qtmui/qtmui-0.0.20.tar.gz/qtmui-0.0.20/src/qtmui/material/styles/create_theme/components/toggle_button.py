from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def toggle_button(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == 'light'
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    return {
        "PyToggleButton": {
            "styles": {
                "root": lambda ownerState: {
                    **{
                        "default": {
                            "selected": {
                                borderColor: theme.palette.grey._500,
                                boxShadow: f"0 0 0 0.5px {theme.palette.grey._500}",
                            }
                        },
                    },
                    **{
                        f"{_color}": {
                            "slots": {
                                "hover": {
                                    borderColor: alpha(getattr(theme.palette, _color).main, 0.48),
                                    backgroundColor: alpha(getattr(theme.palette, _color).main, theme.palette.action.hoverOpacity),
                                }
                            },
                            "props": {
                                "disabled": {
                                    "selected": {
                                        color: theme.palette.action.disabled,
                                        backgroundColor: theme.palette.action.selected,
                                        borderColor: theme.palette.action.disabledBackground,
                                    }
                                }
                            },

                        }
                        for _color in COLORS
                    }
                },
            },
        },
        "PyToggleButtonGroup": {
            "styles": {
                "root": {
                    borderRadius: theme.shape.borderRadius,
                    backgroundColor: theme.palette.background.paper,
                    border: f"solid 1px {alpha(theme.palette.grey._500, 0.08)}",
                },
                "grouped": {
                    m: 4,
                    "props": {
                        "toggleButtonSelected": {
                            boxShadow: "none",
                        },
                        "notFirstOfType": {
                            borderRadius: theme.shape.borderRadius,
                            borderColor: "transparent",
                        },
                        "notLastOfType": {
                            borderRadius: theme.shape.borderRadius,
                            borderColor: "transparent",
                        },
                    }
                },
            },
        },
    }
