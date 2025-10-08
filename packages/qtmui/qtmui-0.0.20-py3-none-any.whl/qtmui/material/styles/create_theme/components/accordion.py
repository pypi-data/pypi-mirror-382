from typing import TYPE_CHECKING, Optional


from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState

class AccordionStyle:
    PyAccordion: str = "" 
    PyAccordionSummary: str = "" 



def accordion(_theme) -> AccordionStyle:
    theme: ThemeState = _theme

    return {
        # CHECKBOX, RADIO, SWITCH
        'PyAccordion': {
            'styles': {
                'root': {
                    backgroundColor: "transparent",
                    "slots": {
                        'expanded': {
                            borderRadius: theme.shape.borderRadius,
                            backgroundColor: theme.palette.background.neutral,
                            boxShadow: theme.customShadows.z8,
                        },
                        'disabled': {
                            backgroundColor: 'transparent',
                        },
                    }
                },
                
            },
        },
        'PyAccordionSummary': {
            'styles': {
                'root': {
                    
                    paddingLeft: theme.spacing(2),
                    paddingRight: theme.spacing(1),
                    height: "40px",
                    "slots": {
                        'disabled': {
                            opacity: 1,
                            color: theme.palette.action.disabled,
                            typography: {
                                "root": {
                                    color: 'inherit'
                                }
                            }
                        },
                    }
                },

                'expandIconWrapper': {
                    color: 'inherit',
                },
            },
        },
        'PyAccordionDetail': {
            'styles': {
                'root': {
                    fontSize: theme.typography.body2.fontSize,
                    lineHeight: theme.typography.body2.lineHeight,
                    fontWeight: theme.typography.body2.fontWeight,
                },
            },
        },
    }


