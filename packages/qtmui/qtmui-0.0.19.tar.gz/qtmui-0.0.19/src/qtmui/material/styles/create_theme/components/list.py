from typing import TYPE_CHECKING, Optional, Dict

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState

def list(_theme) -> Dict:
    theme: ThemeState = _theme

    lightMode = theme.palette.mode == "light"

    return {
        "PyListItemButton": {
            "styles": {
                "root":  lambda ownerState: {
                    fontSize: theme.typography.button.fontSize,
                    fontWeight: theme.typography.button.fontWeight,
                    p: "8px 16px" if ownerState.get("size") == "small" else "12px 24px" if ownerState.get("size") == "medium" else "16px 32px",
                    "slots": {
                        "hover": {
                            backgroundColor: alpha(theme.palette.grey._300 if lightMode else theme.palette.grey._900, 0.34)
                        },
                        "selected": {
                            backgroundColor: alpha(theme.palette.primary.main, 0.12),
                            "hover": {
                                backgroundColor: alpha(theme.palette.primary.main, 0.24),
                            }
                        }
                    },
                    "props": {
                        "divider": {
                            borderBottom: f"1px solid {theme.palette.grey._500}"
                        },
                        "disableGutters": {
                            paddingLeft: "0px",
                            paddingRight: "0px",
                        },
                    }
                }
            }
        },
        "PyListItemIcon": {
            "styles": {
                "root": lambda ownerState: {
                    "marginRight": 0
                }
            }
        },
        "PyListItemAvatar": {
            "styles": {
                "root": {
                    "marginRight": theme.spacing(1)
                }
            }
        },
        "PyListItemText": {
            "styles": {
                "root": {
                    "margin": 0
                },
                "multiline": {
                    "margin": 0
                }
            }
        }
    }
