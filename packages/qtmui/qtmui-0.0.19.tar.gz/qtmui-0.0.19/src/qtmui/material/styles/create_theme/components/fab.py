from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

COLORS = ["primary", "secondary", "info", "success", "warning", "error"]

def fab(_theme) -> Dict:
    theme: ThemeState = _theme

    lightMode = theme.palette.mode == "light"

    return {
        "PyFab": {
            "styles": {
                "root": {
                    "props": {
                        "smallSize": {
                            borderRadius: "15px"
                        },
                        "mediumSize": {
                            borderRadius: "18px"
                        },
                        "largeSize": {
                            borderRadius: "24px"
                        },
                    }
                }
            }
        }
    }
