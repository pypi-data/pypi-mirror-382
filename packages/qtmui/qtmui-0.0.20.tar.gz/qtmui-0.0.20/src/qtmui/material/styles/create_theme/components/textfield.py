from typing import TYPE_CHECKING, Optional, Dict

from ....system.color_manipulator import alpha
from .properties_name import *

if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

class PyFormLabel:
    focused: str = ""
    error: str = ""
    disabled: str = ""
    filled: str = ""

class TextFieldStyle:
    muiFormHelperText: str = "" # HELPER
    muiFormLabel: Optional[PyFormLabel] = None# LABEL
    muiInputBase: str = "" # BASE
    muiInput: str = "" # # STANDARD
    muiOutlinedInput: str = "" # # OUTLINED
    muiFilledInput: str = "" # # FILLED



def text_field(_theme) -> Dict:
    theme: ThemeState = _theme
    
    _color = {
        'focused': theme.palette.text.primary,
        'active': theme.palette.text.secondary,
        'placeholder': theme.palette.text.disabled,
    }

    # font = {
    #     'label': theme.typography.body1.to_qss_props(),
    #     'value': theme.typography.body2.to_qss_props(), # body2
    # }


    return {
        # HELPER
        'PyFormHelperText': {
            'styles': {
                'root': {
                    marginTop: {theme.spacing(1)}
                }
            },
        },

        # LABEL
        'PyFormLabel': {
            'styles': {
                'root': {
                    subcontrolOrigin: "margin",
                    border: "1px solid rgba(145, 158, 171, 0.16)",
                    left: theme.spacing(1),
                    height: 20,
                    fontSize: '8px',
                    border: 'none',
                    fontWeight: 600,
                    color: theme.palette.text.secondary,
                    backgroundColor: theme.palette.background.paper,

                    "slots": {
                        'active': {
                            color: _color['focused']
                        },
                        'focused': {
                            color: _color['focused']
                        },
                        'error': {
                            color: theme.palette.error.main
                        },
                        'disabled': {
                            color: theme.palette.text.disabled
                        },
                        'filled': {
                            backgroundColor: "transparent",
                        },
                        'standardVariant': {
                            marginLeft: "0px",
                        },
                    },
                },
            }
        },

        # BASE
        'PyInputBase': {
            'styles': {
                'root': {
                    border: "none",
                    fontWeight: 600,
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    color: theme.palette.text.primary,
                },
                'placeholder': {
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    opacity: 1,
                    color: _color['placeholder']
                }
            },
        },

        # STANDARD
        'PyStandardInput': {
            'styles': {
                'root': {
                    backgroundColor: "transparent",
                    fontWeight: 600,
                    color: theme.palette.text.primary,
                    border: "1px solid transparent",
                    borderBottom: f"1px solid {alpha(theme.palette.grey._500, 0.32)}" ,
                    borderRadius: '0px',
                    paddingLeft: '0px!important', # NOT WORK
                    "slots": {
                        'hover': {
                            borderBottomColor: _color['active']
                        },
                        'focused': {
                            borderBottomColor: _color['focused']
                        },
                        'error': {
                            borderBottomColor: theme.palette.error.main
                        },
                        'multiple': {
                            paddingRight: "0px"
                        },
                        'hasStartAdornment': {
                            paddingLeft: f"{theme.spacing(3)}"
                        },
                        'standardVariant': {
                            paddingLeft: "0px",
                        },
                    }
                },
                'typography': {
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: 600,
                    color: _color['active'],
                },
            },
        },

        # OUTLINED
        'PyOutlinedInput': {
            'styles': {
                'root': {
                    margin: "0px",
                    marginTop: "10px",
                    backgroundColor: "transparent",
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: 600,
                    color: theme.palette.text.primary,
                    border: f"1px solid {alpha(theme.palette.grey._500, 0.2)}",
                    borderRadius: f'{theme.shape.borderRadius}px',
                    "slots": {
                        'hover': {
                            borderColor: _color['active']
                        },
                        'focused': {
                            borderColor: _color['focused']
                        },
                        'error': {
                            color: theme.palette.error.main,
                            borderColor: theme.palette.error.main
                        },
                        'disabled': {
                            borderColor: theme.palette.action.disabledBackground
                        },
                        'multiple': {
                            paddingRight: "0px"
                        },
                        'hasStartAdornment': {
                            paddingLeft: f"{theme.spacing(3)}"
                        },

                    }
                },

                'typography': {
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: 600,
                    color: _color['active'],
                },
                'placeholder': {
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    opacity: 1,
                    color: _color['placeholder'],
                }
            },
        },

        # FILLED
        'PyFilledInput': {
            'styles': {
                'root': {
                    backgroundColor: alpha(theme.palette.grey._500, 0.16),
                    fontWeight: 600,
                    borderRadius: theme.shape.borderRadius,
                    color: theme.palette.text.primary,
                    "slots": {
                        'hover': {
                            backgroundColor: alpha(theme.palette.grey._500, 0.16)
                        },
                        'focused': {
                            backgroundColor: alpha(theme.palette.grey._500, 0.16)
                        },
                        'error': {
                            backgroundColor: alpha(theme.palette.error.main, 0.08)
                        },
                        'errorFocused': {
                            backgroundColor: alpha(theme.palette.error.main, 0.16)
                        },
                        'disabled': {
                            backgroundColor: theme.palette.action.disabledBackground
                        },
                        'multiple': {
                            paddingRight: "0px"
                        },
                        'hasStartAdornment': {
                            paddingLeft: f"{theme.spacing(3)}"
                        },
                        'filled-small-size': {
                            height: 30,
                            paddingBottom: "2px",
                        },
                        'filled-medium-size': {
                            height: 34,
                            paddingBottom: "4px",
                        },
                    }
                },
                'typography': {
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: 600,
                    color: _color['active'],
                    paddingLeft: '8px'
                },
            },
        },
        'MuiInputSize': {
            'styles': {
                'small': {
                    fontSize: 13,
                    paddingLeft: 8,
                    paddingRight: 8,
                    'no-multiple': {
                        # height: 20, # 30
                        minHeight: 20,
                        maxHeight: 20, 
                    },
                    'filledVariant': {
                        # height: 22, #32 # mui 4
                        minHeight: 22,
                        maxHeight: 22, 
                    },
                    'dateTimeType': {
                        paddingLeft: f"{theme.spacing(3)}"
                    }
                },
                'medium': {
                    paddingLeft: 12,
                    paddingRight: 12,
                    'no-multiple': {
                        minHeight: 36,
                        maxHeight: 36,
                    },
                    'filledVariant': {
                        # height: 38, # mui 4
                        minHeight: 38,
                        maxHeight: 38,
                    },
                    'dateTimeType': {
                        paddingLeft: f"{theme.spacing(4)}"
                    }
                },

            }
        }
    }
