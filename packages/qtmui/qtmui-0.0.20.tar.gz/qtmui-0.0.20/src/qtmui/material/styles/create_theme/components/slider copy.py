from typing import Dict
from qtmui.material.styles.create_theme.theme_reducer import ThemeState

def slider(theme: ThemeState) -> Dict:
    light_mode = theme.palette.mode == 'light'

    return {
        "MuiSlider": {
            "styleOverrides": {
                "root": {
                    f"&.{sliderClasses.disabled}": {
                        "color": theme.palette.action.disabled,
                    },
                },
                "rail": {
                    "opacity": 0.32,
                },
                "markLabel": {
                    "fontSize": 13,
                    "color": theme.palette.text.disabled,
                },
                "valueLabel": {
                    "borderRadius": 8,
                    "backgroundColor": theme.palette.grey[800 if light_mode else 700],
                },
            },
        },
    }
