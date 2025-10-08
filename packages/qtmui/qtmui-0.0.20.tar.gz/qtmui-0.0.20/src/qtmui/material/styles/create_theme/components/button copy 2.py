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
                    paddingTop: "0px"
                },
            },
        },
        'PyButtonContained': {
            'styles': {
                'root': {
                    **{
                        _color: {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                            backgroundColor: getattr(theme.palette, _color).main,
                            "textContent": {
                                color: getattr(theme.palette, _color).contrastText
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: getattr(theme_palette, _color).dark if lightMode else getattr(theme_palette, _color).light,
                                }
                            },
                        }
                        for _color in COLORS
                    },
                    **{
                        "inherit": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                            "textContent": {
                                color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                }
                            },
                        },
                    },
                    **{
                        "default": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                            "textContent": {
                                color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: theme.palette.common.white if not lightMode else theme.palette.grey._800,
                                }
                            },
                        },
                    },
                },
                'icon': {
                    'opacity': 1,
                },
            },
        },
        'PyButtonOutlined': {
            'styles': {
                'root': {
                    **{
                        _color: {
                            border: f"1px solid {alpha(getattr(theme.palette, _color).main, 0.32)}",
                            borderRadius: "4px",
                            backgroundColor: "transparent",
                            "textContent": {
                                color: getattr(theme.palette, _color).main
                            },
                            "slots": {
                                "hover": {
                                    borderColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                }
                            },
                        }
                        for _color in COLORS
                    },
                    **{
                        "inherit": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            borderColor: alpha(theme_palette.grey._500, 0.32),
                            "textContent": {
                                color: theme.palette.common.white if not lightMode else theme.palette.grey._800
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: theme_palette.action.hover,
                                }
                            },
                        },
                    },
                    **{
                        "default": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            borderColor: alpha(theme_palette.grey._500, 0.32),
                            "textContent": {
                                color: theme.palette.common.white if not lightMode else theme.palette.grey._800
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: theme_palette.action.hover,
                                }
                            },
                        },
                    },
                },
                
            },
        },
        'PyButtonSoft': {
            'styles': {
                'root': {
                    **{
                        _color: {
                            border: f"1px solid transparent",
                            borderRadius: "4px",
                            backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                            "textContent": {
                                color: getattr(theme_palette, _color).dark if lightMode else getattr(theme_palette, _color).light
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: alpha(getattr(theme.palette, _color).main, 0.32),
                                }
                            },
                        }
                        for _color in COLORS
                    },
                    **{
                        "inherit": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            backgroundColor: alpha(theme_palette.grey._500, 0.08),
                            "textContent": {
                                color: theme.palette.common.white if not lightMode else theme.palette.grey._800
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: alpha(theme_palette.grey._500, 0.24),
                                }
                            },
                        },
                    },
                    **{
                        "default": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            backgroundColor: alpha(theme_palette.grey._500, 0.08),
                            "textContent": {
                                color: theme.palette.common.white if not lightMode else theme.palette.grey._800
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: alpha(theme_palette.grey._500, 0.24),
                                }
                            },
                        },
                    },
                },

            },
        },
        'PyButtonText': {
            'styles': {
                'root': {
                    **{
                        _color: {
                            border: f"1px solid transparent",
                            borderRadius: "4px",
                            backgroundColor: "transparent",
                            "textContent": {
                                color: getattr(theme.palette, _color).main
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: alpha(getattr(theme.palette, _color).main, 0.08),
                                }
                            },
                        }
                        for _color in COLORS
                    },
                    **{
                        "inherit": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            borderColor: alpha(theme_palette.grey._500, 0.32),
                            "textContent": {
                                color: theme.palette.common.white if not lightMode else theme.palette.grey._800
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: theme_palette.action.hover,
                                }
                            },
                        },
                    },
                    **{
                        "default": {
                            border: "1px solid transparent",
                            borderRadius: "4px",
                            borderColor: alpha(theme_palette.grey._500, 0.32),
                            "textContent": {
                                color: theme.palette.grey._500
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: theme_palette.action.hover,
                                }
                            },
                        },
                    },
                },

            },
        },
        'PyButtonDisabled': {
            'styles': {
                'root': {
                    color: theme_palette.text.disabled,
                    backgroundColor: theme_palette.action.disabledBackground,
                    'textVariant': {
                        borderColor: "transparent",
                        backgroundColor: "transparent",
                    },
                    'softVariant': {
                        backgroundColor: theme_palette.action.disabledBackground,
                    }
                }
            },
        },

        'PyButtonSize': {
            'styles': {
                'small': {
                    height: '30px',
                    fontSize: '13px',
                    paddingLeft: '8px',
                    paddingRight: '8px',
                    'textVariant': {
                        paddingLeft: '5px', # mui 4
                        paddingRight: '5px', # mui 4
                    }
                },
                'medium': {
                    height: '36px', # xem lai
                    paddingLeft: '12px',
                    paddingRight: '12px',
                    'textVariant': {
                        paddingLeft: '8px',
                        paddingRight: '8px',
                    }
                },
                'large': {
                    height: '48px',
                    fontSize: '15px',
                    paddingLeft: '16px',
                    paddingRight: '16px',
                    'textVariant': {
                        paddingLeft: '14px', # mui 10
                        paddingRight: '14px', # mui 10
                    }
                }
            }
        }
    }
