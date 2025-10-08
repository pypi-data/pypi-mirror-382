from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def tree_view(_theme) -> Dict:
    theme: ThemeState = _theme

    lightMode = theme.palette.mode == "light"

    return {
        # TreeWidget
        "PyTreeWidget": {
            "styles": {
                "root": {
                    
                }
            }
        },
        "PyTreeWidgetList": {
            "styles": {
                "root": {
                    
                }
            }
        },
        "PyTreeWidgetItem": {
            "styles": {
                "root": {
                    
                }
            }
        },
        "PyTreeView": {
            "styles": {
                "root": {
                    
                }
            }
        },
        "PyTreeList": {
            "styles": {
                "root": {

                }
            }
        },
        "PyTreeItem": {
            "styles": {
                "root": {

                }
            }
        },
    }
