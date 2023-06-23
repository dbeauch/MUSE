import sys
import os

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from pages import home, cells, surfaces
from template_handler import *

# TODO: Make console_output and select dropdown into a dcc.Store to store per user to keep after refresh

# Sizes and Colors
navbar_width = '15vw'
console_height = '20vh'
console_banner_height = '0.1vh'
page_background = '#D3D3D3'
navbar_color = '#993300'


# Only runs preprocessing operations for the main server process not for monitor process
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    sys.setrecursionlimit(8000)
    template = TemplateHandler()
    # template.read_template('../mcnp_templates/test.i')
    template.read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')
else:
    template = TemplateHandler()


app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUX]
)

banner = html.Header(
    "Py2MCNP Editor",
    style={
        'backgroundColor': navbar_color,
        'color': 'white',
        'padding': '0px',
        'fontSize': '3vh',
        'textAlign': 'center'
    }
)

navbar = html.Div([
    banner,
    dbc.Nav(
        [
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Cell Cards", href="/cells", active="exact"),
            dbc.NavLink("Surface Cards", href="/surfaces", active="exact"),
            dbc.NavLink("Material Cards", href="/materials", active="exact"),
            dbc.NavLink("Option Cards", href="/options", active="exact"),
        ],
        vertical=True,
        pills=True,
        style={'margin': '20px'},
    ),
], style={
    'color': 'black',
    'backgroundColor': navbar_color,
    'width': navbar_width,
    'height': '100vh',
    'position': 'fixed'
})

console = html.Div([
    dbc.Row([
        dbc.Col("Console", width=3),
        dbc.Col(
            dcc.Input(id='file_path', type='text', placeholder='File path', debounce=True),
            width=2
        ),
        dbc.Col(width=1),
        dbc.Col(dcc.Checklist(id='element_comments', options=['Element Comments'], value=['Element Comments']), width=2),
        dbc.Col(width=2),
        dbc.Col(html.Button("-", id="console_toggler"), width=2)
    ], align='center',
        style={
            'marginTop': 20,
            'backgroundColor': 'black',
            'color': 'white',
            'padding': console_banner_height,
            'fontSize': '15px'
        },
        className='g-0'),

    dbc.Collapse(
        html.Div(
            id='console_output',
            style={
                'backgroundColor': '#333333',
                'color': '#A9A9A9',
                'border': '1px solid black',
                'height': console_height,
                'overflow': 'scroll'
            },
        ),
        id='console_output_window',
        is_open=True,
    )
],
    style={
        'marginLeft': navbar_width,
        'position': 'fixed',
        'bottom': 0,
        'width': 'calc(100%)'
    }
)

content = html.Div(
    id="page_content",
    style={'marginLeft': navbar_width, 'backgroundColor': page_background}
)

app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(navbar, width='auto'),
        dbc.Col([
            content,
            html.Hr(),
            html.Button('Apply Changes', id='cell_apply_button', n_clicks=0),
            console
        ])
    ], justify="start", className="g-0")
])


@app.callback(
    Output('page_content', 'children'),
    Output("console_output_window", "is_open", allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call=True,
)
def display_page(pathname):
    if pathname == '/':
        return home.layout(template, page_background), False
    elif pathname == '/cells':
        return cells.layout(template, page_background), True
    elif pathname == '/surfaces':
        return surfaces.layout(template, page_background), True
    else:
        return '404 Error: This page does not exist...YET!', False


@app.callback(
    Output('console_output_window', 'is_open', allow_duplicate=True),
    Input('console_toggler', 'n_clicks'),
    State('console_output_window', 'is_open'),
    prevent_initial_call=True,
)
def toggle_console(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
