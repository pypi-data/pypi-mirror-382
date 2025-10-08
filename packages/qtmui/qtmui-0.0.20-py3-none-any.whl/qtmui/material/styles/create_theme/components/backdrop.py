from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from ....system.color_manipulator import alpha

def app_bar(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyBackdrop': {
            'styles': {
                'root': {
                    backgroundColor: alpha(theme.palette.grey._900, 0.8),
                }
            }
        }
    }
