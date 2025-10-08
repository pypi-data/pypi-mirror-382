from typing import Dict, TYPE_CHECKING

from .properties_name import *

if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

def dialog(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme
    return {
        'PyDialog': {
            'styles': {
                'paper': {
                    "root": {
                        boxShadow: theme.customShadows.dialog,
                        
                        borderRadius: theme.shape.borderRadius * 2,
                        backgroundColor: theme.palette.background.paper,
                        'slots': {
                            'fullScreen': {
                                m: theme.spacing(2),
                            }
                        }
                    }
                },
                'paperFullScreen': {
                    borderRadius: 0,
                },
            },
        },
        'PyDialogTitle': {
            'styles': {
                'root': {
                    p: theme.spacing(3),
                },
            },
        },
        'PyDialogContent': {
            'styles': {
                'root': {
                    p: theme.spacing(0, 3),
                },
                'dividers': {
                    borderTop: 0,
                    borderBottomStyle: 'dashed',
                    paddingBottom: theme.spacing(3),
                },
            },
        },
        'PyDialogActions': {
            'styles': {
                'root': {
                    p: theme.spacing(3),
                    '& > :not(:first-of-type)': {
                        marginLeft: theme.spacing(1.5),
                    },
                },
            },
        },
    }
