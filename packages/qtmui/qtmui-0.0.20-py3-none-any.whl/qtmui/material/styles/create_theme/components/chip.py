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


def chip(_theme):
    theme: ThemeState = _theme

    lightMode = theme.palette.mode == 'light'
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    return {
        'PyChip': {
            'styles': {
                'root': {
                    **{
                        "default": {
                            color: "red",
                            "fontWeight": 500,
                            "borderRadius": theme.shape.borderRadius,
                            "textContent": {
                                fontSize: theme.typography.button.fontSize,
                                fontWeight: theme.typography.button.fontWeight,
                                lineHeight: theme.typography.button.lineHeight,
                            },
                            "deleteIcon": {
                                'size': 16,
                                'border-radius': '8px',
                                "props": {
                                    "filledVariant": {
                                        backgroundColor: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        "hover": {
                                            backgroundColor: alpha(theme.palette.common.white, 0.24) if lightMode else alpha(theme.palette.grey._800, 0.24),
                                        }
                                    },
                                    "outlinedVariant": {
                                        backgroundColor: theme.palette.grey._500,
                                        "hover": {
                                            backgroundColor: theme.palette.common.black if lightMode else theme.palette.common.white,
                                        }
                                    },
                                    "softVariant": {
                                        backgroundColor: theme.palette.grey._500,
                                        "hover": {
                                            backgroundColor: theme.palette.common.black if lightMode else theme.palette.common.white,
                                        }
                                    },
                                },
                            },
                            "slots": {
                                "hover": {
                                    backgroundColor: "transparent"
                                }
                            },
                            "props": {
                                "smallSize": {
                                    p: "1px 2px"
                                },
                                "mediumSize": {
                                    p: "2px 4px"
                                },
                                "filledVariant": {
                                    color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                    backgroundColor: theme.palette.text.primary,
                                    "slots": {
                                        "hover": {
                                            backgroundColor: theme.palette.grey._700 if lightMode else theme.palette.grey._100,
                                        }
                                    },
                                    "classes": {
                                        "icon": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    }
                                },
                                "outlinedVariant": {
                                    color: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                                    backgroundColor: "transparent",
                                    border: f"1px solid {alpha(theme.palette.grey._500, 0.16)}",
                                    "slots": {
                                        "hover": {
                                            backgroundColor: "transparent"
                                        }
                                    },
                                    "classes": {
                                        "icon": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    }
                                },
                                "softVariant": {
                                    color: theme.palette.text.primary,
                                    backgroundColor: alpha(theme.palette.grey._500, 0.16),
                                    "slots": {
                                        "hover": {
                                            backgroundColor: alpha(theme.palette.grey._500, 0.32),
                                        }
                                    },
                                    "classes": {
                                        "icon": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    }
                                },

                            },
                        }
                    },
                    **{
                        f"{_color}": {
                            color: "red",
                            "fontWeight": 500,
                            "border": "1px solid transparent",
                            "borderRadius": theme.shape.borderRadius,
                            "textContent": {
                                fontSize: theme.typography.button.fontSize,
                                fontWeight: theme.typography.button.fontWeight,
                                lineHeight: theme.typography.button.lineHeight,
                            },
                            "deleteIcon": {
                                borderRadius: '8px',
                                'size': 16,
                                "props": {
                                    "filledVariant": {
                                        backgroundColor: alpha(theme.palette.common.white, 0.64) if lightMode else alpha(theme.palette.grey._800, 0.64),
                                        "hover": {
                                            backgroundColor: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    },
                                    "outlinedVariant": {
                                        backgroundColor: alpha(getattr(theme.palette, _color).light, 0.64),
                                        "hover": {
                                            backgroundColor: getattr(theme.palette, _color).light,
                                        }
                                    },
                                    "softVariant": {
                                        backgroundColor: alpha(getattr(theme.palette, _color).dark, 0.64),
                                        "hover": {
                                            backgroundColor: getattr(theme.palette, _color).dark,
                                        }
                                    },
                                },
                            },
                            "slots": {
                                "hover": {
                                }
                            },
                            "props": {
                                "smallSize": {
                                    p: "1px 2px"
                                },
                                "mediumSize": {
                                    p: "2px 4px"
                                },
                                "filledVariant": {
                                    color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                    backgroundColor: getattr(theme.palette, _color).main,
                                    "slots": {
                                        "hover": {
                                            backgroundColor: getattr(theme.palette, _color).dark,
                                        }
                                    },
                                    "classes": {
                                        "icon": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    }
                                },
                                "outlinedVariant": {
                                    color: getattr(theme.palette, _color).dark if lightMode else getattr(theme.palette, _color).light,
                                    backgroundColor: "transparent",
                                    borderColor: getattr(theme.palette, _color).main,
                                    "slots": {
                                        "hover": {
                                            backgroundColor: alpha(getattr(theme.palette, _color).main, 0.08),
                                        }
                                    },
                                    "classes": {
                                        "icon": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    }
                                },
                                "softVariant": {
                                    color: getattr(theme.palette, _color).dark if lightMode else getattr(theme.palette, _color).light,
                                    backgroundColor: alpha(getattr(theme.palette, _color).main, 0.16),
                                    "slots": {
                                        "hover": {
                                            backgroundColor: alpha(getattr(theme.palette, _color).main, 0.32),
                                        }
                                    },
                                    "classes": {
                                        "icon": {
                                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                                        }
                                    }
                                },

                            },
                        } 
                        for _color in COLORS
                    }
                },
                "avatar": {
                    color: theme.palette.text.primary,
                },
                "icon": {

                }
            },
        },

    }
