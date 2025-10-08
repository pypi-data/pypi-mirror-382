from typing import TYPE_CHECKING, Optional

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState


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
