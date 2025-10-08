from typing import TYPE_CHECKING, Optional

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState
    from qtmui.material.styles.create_theme.create_palette import Palette


def label(_theme):
    # Khởi tạo các thông tin cần thiết
    theme: ThemeState = _theme

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'
    
    return {
        'PyLabel': {
            'styles': {
                'root': {
                    **{
                        _color: {
                            border: "2px solid transparent",
                            borderRadius: "4px",
                            p: "4px",
                            fontSize: theme.typography.button.fontSize,
                            fontWeight: theme.typography.button.fontWeight,
                            "props": {
                                "variant": {
                                    "filled": {
                                        color: theme.palette.getContrastText(getattr(theme.palette, _color).main),
                                        backgroundColor: getattr(theme.palette, _color).main,
                                    },
                                    "outlined": {
                                        color: getattr(theme.palette, _color).main,
                                        borderColor: getattr(theme.palette, _color).main,
                                        p: "3px",
                                    },
                                    "soft": {
                                        backgroundColor: alpha(getattr(theme.palette, _color).main, 0.24),
                                        color: getattr(theme.palette, _color).dark if lightMode else getattr(theme.palette, _color).light,
                                    },
                                }
                            }
                        }
                        for _color in COLORS
                    },

                    **{
                        "default": {
                            border: "2px solid transparent",
                            borderRadius: "4px",
                            p: "4px",
                            fontSize: theme.typography.button.fontSize,
                            fontWeight: theme.typography.button.fontWeight,
                            "props": {
                                "variant": {
                                    "filled": {
                                        color: theme.palette.common.white if lightMode else theme.palette.common.black,
                                        backgroundColor: theme.palette.common.black if lightMode else theme.palette.common.white,
                                    },
                                    "outlined": {
                                        color: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                                        borderColor: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                                        p: "3px",
                                    },
                                    "soft": {
                                        backgroundColor: alpha(theme.palette.grey._600, 0.24) if lightMode else alpha(theme.palette.grey._400, 0.24),
                                        color: theme.palette.grey._600 if lightMode else theme.palette.grey._400,
                                    },
                                }
                            }
                        },
                    },
                },
            },
        },
    }
