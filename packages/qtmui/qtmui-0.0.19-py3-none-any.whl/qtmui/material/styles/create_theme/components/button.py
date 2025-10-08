from typing import TYPE_CHECKING, Optional

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState
    from qtmui.material.styles.create_theme.create_palette import Palette


def button(_theme):
    # Khởi tạo các thông tin cần thiết
    theme: ThemeState = _theme
    theme_palette: Palette = theme.palette

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'
    
    
    return {
        'PyButton': {
            'styles': {
                'root': {
                    "colorStyle": {
                        **{
                            _color: {
                                "props": {
                                    "containedVariant": {
                                        color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        backgroundColor: getattr(theme.palette, _color).main,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: getattr(theme_palette, _color).dark if lightMode else getattr(theme_palette, _color).light,
                                            },
                                            "checked": {
                                                backgroundColor: getattr(theme_palette, _color).dark if lightMode else getattr(theme_palette, _color).light,
                                            },
                                        }
                                    },
                                    "outlinedVariant": {
                                        border: f"1px solid {alpha(getattr(theme.palette, _color).main, 0.32)}",
                                        backgroundColor: "transparent",
                                        color: getattr(theme.palette, _color).main,
                                        "slots": {
                                            "hover": {
                                                borderColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                            },
                                            "checked": {
                                                borderColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                            },
                                        }
                                    },
                                    "textVariant": {
                                        border: f"1px solid transparent",
                                        backgroundColor: "transparent",
                                        color: getattr(theme.palette, _color).main,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                            },
                                            "checked": {
                                                backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                            },
                                        }
                                    },
                                    "softVariant": {
                                        border: f"1px solid transparent",
                                        backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                        color: getattr(theme_palette, _color).dark if lightMode else getattr(theme_palette, _color).light,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: alpha(getattr(theme.palette, _color).main, 0.32),
                                            },
                                            "checked": {
                                                backgroundColor: alpha(getattr(theme.palette, _color).main, 0.32),
                                            },
                                        }
                                    },
                                    "disabledVariant": {
                                        border: f"1px solid transparent",
                                        backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                        color: getattr(theme_palette, _color).dark if lightMode else getattr(theme_palette, _color).light,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: alpha(getattr(theme.palette, _color).main, 0.32),
                                            },
                                            "checked": {
                                                backgroundColor: alpha(getattr(theme.palette, _color).main, 0.32),
                                            },
                                        }
                                    },
                                },
                            }
                            for _color in COLORS
                        },
                        **{
                            "default": {
                                "props": {
                                    "containedVariant": {
                                        border: "1px solid transparent",
                                        backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                        color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                            },
                                            "checked": {
                                                backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                            },
                                        }
                                    },
                                    "outlinedVariant": {
                                        border: "1px solid transparent",
                                        borderColor: alpha(theme_palette.grey._500, 0.32),
                                        color: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: theme_palette.action.hover,
                                            },
                                            "checked": {
                                                backgroundColor: theme_palette.action.hover,
                                            },
                                        }
                                    },
                                    "textVariant": {
                                        border: "1px solid transparent",
                                        borderColor: "transparent",
                                        color: theme.palette.grey._500,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: theme_palette.action.hover,
                                            },
                                            "checked": {
                                                backgroundColor: theme_palette.action.hover,
                                            },
                                        }
                                    },
                                    "softVariant": {
                                        border: "1px solid transparent",
                                        backgroundColor: alpha(theme_palette.grey._500, 0.08),
                                        color: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                        "slots": {
                                            "hover": {
                                                backgroundColor: alpha(theme_palette.grey._500, 0.24),
                                            },
                                            "checked": {
                                                backgroundColor: alpha(theme_palette.grey._500, 0.24),
                                            },
                                        }
                                    },
                                },
                            },
                        },
                    },
                    "size": {
                        'small': {
                            fontSize: theme.typography.button.fontSize,
                            lineHeight: theme.typography.button.lineHeight,
                            fontWeight: theme.typography.button.fontWeight,
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            height: 30,
                            fontSize: 13,
                            paddingLeft: 8,
                            paddingRight: 8,
                            'textVariant': {
                                paddingLeft: 4, # mui 4
                                paddingRight: 4, # mui 4
                            }
                        },
                        'medium': {
                            fontSize: theme.typography.button.fontSize,
                            lineHeight: theme.typography.button.lineHeight,
                            fontWeight: theme.typography.button.fontWeight,
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            height: 36, # xem lai
                            paddingLeft: 12,
                            paddingRight: 12,
                            'textVariant': {
                                paddingLeft: 8,
                                paddingRight: 8,
                            }
                        },
                        'large': {
                            fontSize: theme.typography.button.fontSize,
                            lineHeight: theme.typography.button.lineHeight,
                            fontWeight: theme.typography.button.fontWeight,
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            height: 48,
                            fontSize: 15,
                            paddingLeft: 16,
                            paddingRight: 16,
                            'textVariant': {
                                paddingLeft: 14, # mui 10
                                paddingRight: 14, # mui 10
                            }
                        }
                    },
                },
                'icon': {
                    'opacity': 1,
                },
            },
        },


    }
