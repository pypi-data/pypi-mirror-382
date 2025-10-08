from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def menu(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == "light"

    return {
        'PyMenu': {
            'styles': {
                "root": {
                    backgroundColor: "transparent",
                },
                "container": {
                    backgroundColor: theme.palette.background.paper,
                    borderRadius: theme.spacing(1),
                    border: f"1px solid {alpha(theme.palette.grey._500, 0.14)}"
                }
            },
        },
        'PyMenuItem': {
            'styles': {
                "root": {
                    p: theme.spacing(0.75, 1),
                    borderRadius: f"{theme.shape.borderRadius * 0.75}px",
                    fontSize: theme.typography.button.fontSize,
                    fontWeight: theme.typography.button.fontWeight,
                    lineHeight: theme.typography.button.lineHeight,
                    textAlign: "left",
                    minHeight: 38,
                    # color: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                    color: theme.palette.grey._700 if lightMode else theme.palette.grey._200,
                    "slots": {
                        "hover": {
                            backgroundColor: alpha(theme.palette.grey._300 if lightMode else theme.palette.grey._900, 0.34)
                        },
                        # "selected": {
                        #     backgroundColor: theme.palette.action.selected,
                        #     'hover': {
                        #         backgroundColor: theme.palette.action.hover,
                        #     },
                        # },
                        "selected": {
                            backgroundColor: alpha(theme.palette.primary.main, 0.24),
                            'hover': {
                                backgroundColor: alpha(theme.palette.primary.main, 0.36),
                            },
                        },
                    },
                    "props": {
                        "notLastOfType": {
                            marginBottom: 4
                        }
                    }
                },
                "checkbox": {
                    p: theme.spacing(0.5),
                    marginLeft: theme.spacing(-0.5),
                    marginRight: theme.spacing(0.5),
                },
                "autocomplete": {
                    backgroundColor: theme.palette.action.selected,
                    'hover': {
                        backgroundColor: theme.palette.action.hover,
                    },
                },
                "divider": {
                    m: theme.spacing(0.5, 0),
                },
            },
        },
    }
