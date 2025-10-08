from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def loading_button(_theme) -> Dict:
    theme: ThemeState = _theme

    return {
        "PyLoadingButton": {
            "styles": {
                "root": lambda ownerState: {
                    "props": {
                        "softVariant": {
                            "loadingIndicatorStart": {
                                "left": 10
                            },
                            "loadingIndicatorEnd": {
                                "right": 14
                            },
                        },
                        "smallSize": {
                            "loadingIndicatorStart": {
                                "left": 10
                            },
                            "loadingIndicatorEnd": {
                                "right": 10
                            },
                        }
                    }
                }
            }
        }
    }
