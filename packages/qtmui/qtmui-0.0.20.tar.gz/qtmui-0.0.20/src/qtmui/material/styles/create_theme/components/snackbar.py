from typing import TYPE_CHECKING, Optional

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState


def snackbar(_theme):
    theme: ThemeState = _theme

    COLORS = ['info', 'success', 'warning', 'error']

    lightMode = theme.palette.mode == 'light'

    return {
        'Snackbar': {
            'styles': {
                "root": {
                    **{
                        "default": {
                            border: f"1px solid {theme.palette.grey._500}",
                            borderRadius: "4px",
                            backgroundColor: theme.palette.background.paper,
                            "titleLabel": {
                                fontWeight: theme.typography.subtitle1.fontWeight,
                                lineHeight: theme.typography.subtitle1.lineHeight,
                                backgroundColor: "transparent",
                                color: theme.palette.text.primary
                            },
                            "contentLabel": {
                                fontWeight: theme.typography.body1.fontWeight,
                                lineHeight: theme.typography.body1.lineHeight,
                                backgroundColor: "transparent",
                                color: theme.palette.text.secondary
                            },
                            "props": {
                                "variant": {
                                    f"{_variant}": {
                                        borderWidth: "1px" if _variant == "outlined" else "0px"
                                    }
                                    for _variant in ["outlined", "filled"]
                                }
                            }
                        },
                    },
                    **{
                        _color: {
                            border: f"1px solid {getattr(theme.palette, _color).main}",
                            borderRadius: "4px",
                            backgroundColor: theme.palette.background.paper,
                            "titleLabel": {
                                fontWeight: theme.typography.subtitle1.fontWeight,
                                lineHeight: theme.typography.subtitle1.lineHeight,
                                backgroundColor: "transparent",
                                color: getattr(theme.palette, _color).main
                            },
                            "contentLabel": {
                                fontWeight: theme.typography.body1.fontWeight,
                                lineHeight: theme.typography.body1.lineHeight,
                                backgroundColor: "transparent",
                                color: getattr(theme.palette, _color).main
                            },
                            "props": {
                                "variant": {
                                    f"{_variant}": {
                                        borderWidth: "1px" if _variant == "outlined" else "0px"
                                    }
                                    for _variant in ["outlined", "filled"]
                                }
                            }
                        }
                        for _color in COLORS
                    }
                },
            }
        },

    }
