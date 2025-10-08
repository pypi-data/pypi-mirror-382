from qtmui.material.styles.create_theme.theme_reducer import ThemeState

def app_bar(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyAppBar': {
            'styles': {
                'root': {
                    'boxShadow': 'none',
                }
            }
        }
    }
