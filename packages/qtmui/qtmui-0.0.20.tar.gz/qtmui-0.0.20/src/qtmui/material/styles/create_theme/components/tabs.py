from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

COLORS = ["primary", "secondary", "info", "success", "warning", "error"]

def tabs(_theme) -> Dict:
    theme: ThemeState = _theme

    lightMode = theme.palette.mode == "light"

    return {
        "PyTabWidget": {
            "styles": {
                "root": {

                },
                "pane": {
                    border: 'none',
                    top:'-1px',
                    backgroundColor: 'transparent'
                },
                "label": {
                    color: theme.palette.text.secondary,
                    fontSize: theme.typography.button.fontSize,
                    fontWeight: theme.typography.button.fontWeight,
                    lineHeight: theme.typography.button.lineHeight,
                    "slots": {
                        "hover": {
                            color: theme.palette.text.primary,
                        }
                    }
                }
            }
        },
        "PyTabBar": {
            "styles": {
                "root": {

                },
                "tab": {
                    border: "2px solid transparent",
                    borderBottom: "2px solid transparent",
                    backgroundColor: 'transparent',
                    color: theme.palette.text.secondary,
                    p: "12px 12px",
                    textAlign: "center",
                    fontSize: theme.typography.button.fontSize,
                    fontWeight: theme.typography.button.fontWeight,
                    lineHeight: theme.typography.button.lineHeight,
                    "slots": {
                        "selected" : {
                            borderBottom: f"2px solid {theme.palette.text.primary}",
                            color: theme.palette.text.primary
                        },
                        "notSelected" : {
                            color: theme.palette.text.secondary,
                            borderColor: 'transparent'
                        },

                    },
                    "props": {
                        "hasIcon": {
                            pl: "24px"
                        },
                        "hasIconAndLabel": {
                            pl: "-20px" 
                        },
                    }
                }
            }
        },
    }
