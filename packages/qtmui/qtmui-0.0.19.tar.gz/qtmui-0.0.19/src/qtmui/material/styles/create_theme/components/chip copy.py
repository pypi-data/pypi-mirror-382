from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

class ChipClasses:
    deleteIcon: str = "MuiChip-deleteIcon"
    avatar: str = "MuiChip-avatar"
    icon: str = "MuiChip-icon"
    disabled: str = "Mui-disabled"


class ChipProps:
    color: str
    variant: str


class ChipStyle:
    muiChip: Dict = {}


def chip(theme) -> ChipStyle:

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    def root_styles(owner_state: ChipProps) -> List[Dict]:
        default_color = owner_state.color == "default"
        filled_variant = owner_state.variant == "filled"
        outlined_variant = owner_state.variant == "outlined"
        soft_variant = owner_state.variant == "soft"

        default_style = {
            f"& .{ChipClasses.deleteIcon}": {
                "opacity": 0.48,
                "color": "currentColor",
                "&:hover": {
                    "opacity": 1,
                    "color": "currentColor",
                },
            },
            **(default_color and {
                f"& .{ChipClasses.avatar}": {
                    "color": theme.palette.text.primary,
                },
                **(filled_variant and {
                    "color": theme.palette.common.white if light_mode else theme.palette.grey[800],
                    "backgroundColor": theme.palette.text.primary,
                    "&:hover": {
                        "backgroundColor": theme.palette.grey[700] if light_mode else theme.palette.grey[100],
                    },
                    f"& .{ChipClasses.icon}": {
                        "color": theme.palette.common.white if light_mode else theme.palette.grey[800],
                    },
                }),
                **(outlined_variant and {
                    "border": f"solid 1px {alpha(theme.palette.grey._500, 0.32)}",
                }),
                **(soft_variant and {
                    "color": theme.palette.text.primary,
                    "backgroundColor": alpha(theme.palette.grey._500, 0.16),
                    "&:hover": {
                        "backgroundColor": alpha(theme.palette.grey._500, 0.32),
                    },
                }),
            })
        }

        color_style = [
            {
                **(owner_state.color == color and {
                    f"& .{ChipClasses.avatar}": {
                        "color": theme.palette[color].lighter,
                        "backgroundColor": theme.palette[color].dark,
                    },
                    **(soft_variant and {
                        "color": theme.palette[color]['dark'] if light_mode else theme.palette[color]['light'],
                        "backgroundColor": alpha(theme.palette[color].main, 0.16),
                        "&:hover": {
                            "backgroundColor": alpha(theme.palette[color].main, 0.32),
                        },
                    }),
                })
            } for color in COLORS
        ]

        disabled_state = {
            f"&.{ChipClasses.disabled}": {
                "opacity": 1,
                "color": theme.palette.action.disabled,
                f"& .{ChipClasses.icon}": {
                    "color": theme.palette.action.disabled,
                },
                f"& .{ChipClasses.avatar}": {
                    "color": theme.palette.action.disabled,
                    "backgroundColor": theme.palette.action.disabledBackground,
                },
                **(filled_variant and {
                    "backgroundColor": theme.palette.action.disabledBackground,
                }),
                **(outlined_variant and {
                    "borderColor": theme.palette.action.disabledBackground,
                }),
                **(soft_variant and {
                    "backgroundColor": theme.palette.action.disabledBackground,
                }),
            }
        }

        return [
            default_style,
            *color_style,
            disabled_state,
            {
                "fontWeight": 500,
                "borderRadius": theme.shape.borderRadius,
            },
        ]

    return {
        "MuiChip": {
            "styleOverrides": {
                "root": lambda owner_state: root_styles(owner_state),
            },
        },
    }

def alert(_theme):
    theme: ThemeState = _theme

    COLORS = ['info', 'success', 'warning', 'error']

    lightMode = theme.palette.mode == 'light'

    return {
        'PyAlertStandard': {
            'styles': {
                'root': {
                    f"{_color}": {
                        border: "0px solid transparent",
                        borderRadius: "8px",
                        color: getattr(theme.palette, _color).darker if lightMode else getattr(theme.palette, _color).lighter,
                        backgroundColor: getattr(theme.palette, _color).lighter if lightMode else getattr(theme.palette, _color).darker,
                    } 
                    for _color in COLORS
                },
                'icon': {
                    f"{_color}": {
                        color: getattr(theme.palette, _color).main if lightMode else getattr(theme.palette, _color).lighter,
                        opacity: 1,
                    } 
                    for _color in COLORS
                },

            },
        },
        'PyAlertFilled': {
            'styles': {
                'root': {
                    f"{_color}": {
                        border: "0px solid transparent",
                        borderRadius: "8px",
                        color: getattr(theme.palette, _color).contrastText,
                        backgroundColor: getattr(theme.palette, _color).main,
                    } 
                    for _color in COLORS
                },
                'icon': {
                    opacity: 1,
                },

            },
        },
        'PyAlertOutlined': {
            'styles': {
                'root': {
                    f"{_color}": {
                        backgroundColor: alpha(getattr(theme.palette, _color).main, 0.08),
                        color: getattr(theme.palette, _color).dark if lightMode else getattr(theme.palette, _color).light,
                        border: f"solid 1px {alpha(getattr(theme.palette, _color).main, 0.16)}",
                        borderRadius: "8px",
                    } 
                    for _color in COLORS
                },
                'icon': {
                    f"{_color}": {
                        color: getattr(theme.palette, _color).main,
                        opacity: 1,
                    } 
                    for _color in COLORS
                },
            },
        },
        'PyAlertTitle': {
            'styles': {
                'root': {
                    f"{_color}": {
                        color: getattr(theme.palette, _color).main,
                        marginBottom: theme.spacing(0.5),
                        fontWeight: 700,
                    } 
                    for _color in COLORS
                },
            },
        },
    }
