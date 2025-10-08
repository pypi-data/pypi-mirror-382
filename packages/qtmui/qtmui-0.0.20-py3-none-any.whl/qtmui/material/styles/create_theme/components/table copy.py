from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def table(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == 'light'

    return {
        "PyTableContainer": {
            "styles": {
                "root": {
                    "position": "relative",
                },
            },
        },
        "PyTableRow": {
            "styles": {
                "root": {
                    "slots": {
                        "selected": {
                            "backgroundColor": alpha(theme.palette.primary.dark, 0.04),
                            "hover": {
                                "backgroundColor": alpha(theme.palette.primary.dark, 0.08),
                            },
                        }
                    }, 
                    "props": {
                        "lastOfType": {
                            "tableCellRoot": {
                                borderColor: "transparent",
                            },
                        },
                    }
                },
            },
        },
        "PyTableCell": {
            "styles": {
                "root": {
                    "borderBottomStyle": "dashed",
                },
                "head": {
                    "fontSize": 14,
                    "color": theme.palette.text.secondary,
                    "fontWeight": theme.typography.font_weight_semi_bold,
                    "backgroundColor": theme.palette.background.neutral,
                },
                "stickyHeader": {
                    "backgroundColor": theme.palette.background.paper,
                    "backgroundImage": f"linear-gradient(to bottom, {theme.palette.background.neutral} 0%, {theme.palette.background.neutral} 100%)",
                },
                "paddingCheckbox": {
                    "paddingLeft": theme.spacing(1),
                },
            },
        },
        "PyTablePagination": {
            "styles": {
                "root": {
                    "width": "100%",
                },
                "toolbar": {
                    "height": 64,
                },
                "actions": {
                    "marginRight": 8,
                },
                "select": {
                    "paddingLeft": 8,
                    "slots": {
                        "focus": {
                            borderRadius: theme.shape.borderRadius,
                        },
                    }
                },
                "selectIcon": {
                    "right": 4,
                    "width": 16,
                    "height": 16,
                    "top": "calc(50% - 8px)",
                },
            },
        },
    }
