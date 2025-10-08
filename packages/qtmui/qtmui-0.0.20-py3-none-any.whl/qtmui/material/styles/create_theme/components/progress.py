from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from ....system.color_manipulator import alpha
from .properties_name import *

# Định nghĩa các màu sắc
COLORS = ["primary", "secondary", "info", "success", "warning", "error"]

def progress(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == "light"

    return {
        "PyLinearProgress": {
            "styles": {
                'root': lambda owner_state: {
                    **{
                        _color: {
                            borderRadius: 4,
                            backgroundColor: alpha(getattr(theme.palette, _color).main, 0.24),
                        }
                        for _color in COLORS
                    },

                    **{
                        "default": {
                            borderRadius: 4,
                            backgroundColor: "transparent" if owner_state.get("variant") == "buffer" else theme.palette.common.black if lightMode else theme.palette.common.white
                        }
                    },
                },
                "bar": {
                    backgroundColor: theme.palette.grey._300 if lightMode else theme.palette.grey._700,
                }
            }
        }
    }
