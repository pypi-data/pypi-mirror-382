from typing import TYPE_CHECKING, Optional

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState
    from qtmui.material.styles.create_theme.create_palette import Palette

def pagination(_theme):
    # Khởi tạo các thông tin cần thiết
    theme: ThemeState = _theme

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'
    
    return {
        'PyPagination': {
            'styles': {
                'root': {
                    **{
                        _color: {
                            "item": {
                                "root": {
                                    "slots": {
                                        "selected": {
                                            fontWeight: theme.typography.fontWeightSemiBold,
                                            borderColor: theme.palette.grey._500,
                                            backgroundColor: alpha(theme.palette.grey._500, 0.08)
                                        }
                                    },
                                    "props": {
                                        "filledVariant": {
                                        },
                                        "outlinedVariant": {
                                        },
                                        "softVariant": {
                                            color: getattr(theme.palette, _color).dark if lightMode else getattr(theme.palette, _color).light,
                                            backgroundColor: alpha(getattr(theme.palette, _color).main, 0.08),
                                            "slots": {
                                                "hover": {
                                                    backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                                }
                                            }
                                        },
                                    }

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
                            "item": {
                                "root": {
                                    "slots": {
                                        "selected": {
                                            fontWeight: theme.typography.fontWeightSemiBold,
                                            borderColor: theme.palette.grey._500,
                                            backgroundColor: alpha(theme.palette.grey._500, 0.08)
                                        }
                                    },
                                    "props": {
                                        "filledVariant": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                            backgroundColor: theme.palette.text.primary,
                                            "slots": {
                                                "hover": {
                                                    backgroundColor: theme.palette.grey._700 if lightMode else theme.palette.grey._100,
                                                }
                                            }
                                        },
                                        "outlinedVariant": {
                                            borderColor: alpha(theme.palette.grey._500, 0.24)
                                        },
                                        "softVariant": {
                                        }
                                    }

                                }
                            }
                        },
                    },
                },
            },
        },
    }
