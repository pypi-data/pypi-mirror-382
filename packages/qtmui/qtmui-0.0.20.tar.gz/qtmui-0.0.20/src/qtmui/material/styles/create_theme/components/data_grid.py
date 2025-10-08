from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from ....css import paper

def data_grid(_theme):
    theme: ThemeState = _theme
    paper_styles = paper(theme=theme, dropdown=True)

    return {
        'PyDataGrid': {
            'styles': {
                'root': {
                    borderRadius: 0,
                    'borderWidth': 0,
                    f'& .{tablePaginationClasses.root}': {
                        borderTop: 0,
                    },
                    f'& .{tablePaginationClasses.toolbar}': {
                        height: 'auto',
                    },
                },
                'cell': {
                    'borderBottom': f'1px dashed {theme.palette.divider}',
                },
                'selectedRowCount': {
                    'whiteSpace': 'nowrap',
                },
                'columnSeparator': {
                    'color': theme.palette.divider,
                },
                'toolbarContainer': {
                    'padding': theme.spacing(2),
                    'borderBottom': f'1px dashed {theme.palette.divider}',
                    backgroundColor: theme.palette.background.neutral,
                },
                'paper': {
                    **paper_styles,
                    'padding': 0,
                },
                'menu': {
                    f'& .{paperClasses.root}': {
                        **paper_styles,
                    },
                    f'& .{listClasses.root}': {
                        'padding': 0,
                        f'& .{listItemIconClasses.root}': {
                            'minWidth': 0,
                            marginRight: theme.spacing(2),
                        },
                    },
                },
                'columnHeaders': {
                    borderRadius: 0,
                    backgroundColor: theme.palette.background.neutral,
                },
                'panelHeader': {
                    'padding': theme.spacing(2),
                },
                'panelFooter': {
                    'padding': theme.spacing(2),
                    'justifyContent': 'flex-end',
                    borderTop: f'dashed 1px {theme.palette.divider}',
                    f'& .{buttonClasses.root}': {
                        '&:first-of-type': {
                            'border': f'solid 1px {alpha(theme.palette.grey[500], 0.24)}',
                        },
                        '&:last-of-type': {
                            marginLeft: theme.spacing(1.5),
                            'color': theme.palette.background.paper,
                            backgroundColor: theme.palette.text.primary,
                        },
                    },
                },
                'filterForm': {
                    'padding': theme.spacing(2),
                },
                'filterFormValueInput': {
                    marginLeft: theme.spacing(2),
                },
                'filterFormColumnInput': {
                    marginLeft: theme.spacing(2),
                },
                'filterFormOperatorInput': {
                    marginLeft: theme.spacing(2),
                },
            },
        },
    }
