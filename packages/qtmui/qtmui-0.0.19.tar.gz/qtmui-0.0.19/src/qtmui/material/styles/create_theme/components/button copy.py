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
    # is_light_mode = theme.palette.mode == 'light'
    # is_inherit_color = self._color == 'inherit'
    # is_extended_variant = self._variant == 'extended'
    # is_contained_variant = self._variant == 'contained'
    # is_outlined_variant = self._variant == 'outlined'
    # is_outlined_extended_variant = self._variant == 'outlinedExtended'
    # is_text_variant = self._variant == 'text'
    # is_soft_variant = self._variant == 'soft'
    # is_soft_extended_variant = self._variant == 'softExtended'
    # is_small_size = self._size == 'small'
    # is_medium_size = self._size == 'medium'
    # is_large_size = self._size == 'large'
    
    return {
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
                    height: 30,
                    fontSize: 13,
                    paddingLeft: 8,
                    paddingRight: 8,
                    'textVariant': {
                        paddingLeft: 5, # mui 4
                        paddingRight: 5, # mui 4
                    }
                },
                'medium': {
                    height: 36, # xem lai
                    paddingLeft: 12,
                    paddingRight: 12,
                    'textVariant': {
                        paddingLeft: 8,
                        paddingRight: 8,
                    }
                },
                'large': {
                    height: 48,
                    fontSize: 15,
                    paddingLeft: 16,
                    paddingRight: 16,
                    'textVariant': {
                        paddingLeft: 14, # mui 10
                        paddingRight: 14, # mui 10
                    }
                }
            }
        }
    }
