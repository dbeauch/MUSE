import sys
import os
import datetime

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import webbrowser
from threading import Timer

from pages import home, cells, surfaces, materials, universes, fuel_assemblies, plate, legacy_fuel_assemblies, options
from Template_Editor.controllers.template_handler_instance import template_handler_instance as template

# Sizes and Colors
navbar_width = '15vw'
console_height = '20vh'
console_banner_height = '0.1vh'
page_background = '#D3D3D3'
navbar_color = '#004a80'

# Only runs preprocessing operation for the main server process not for monitor process
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    sys.setrecursionlimit(8000)
    # file_to_read = '../mcnp_templates/NNR/test.i'
    file_to_read = '../mcnp_templates/NNS/burn_Box9_v02_SU_cycle8.i'
    # file_to_read = '../mcnp_templates/NBSR_HEU_720[236]/NBSR_HEU_720.i'
    template.read_template(file_to_read)

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUX]
)

banner = html.Img(
    src="/assets/logo.png",  # replace 'your-logo.png' with the name of your logo file
    style={
        'width': f'calc({navbar_width})',
        'padding': '1vw',
        'textAlign': 'center'
    }
)

navbar = dbc.Container([
    dbc.Row(banner),
    dbc.Row(dbc.Nav(
        [
            dbc.NavLink("Home", href="/", active="exact", class_name="nav-item"),
            dbc.NavLink("Fuel Assembly", href="/assembly", active="exact", class_name="nav-item"),
            dbc.NavLink("Plate Maker", href="/plate", active="exact", class_name="nav-item"),
            dbc.NavLink("Legacy Assembly", href="/legacy_assembly", active="exact", class_name="nav-item"),
            dbc.Card(
                [
                    dbc.NavLink("\u25BC Card Views ", id="card-views-toggle", class_name="nav-item"),
                    dbc.Collapse(
                        id="card-views-collapse",
                        children=[
                            dbc.NavLink("Cell Cards", href="/cells", active="exact", class_name="nav-item", style={"paddingLeft": "40px"}),
                            dbc.NavLink("Surface Cards", href="/surfaces", active="exact", class_name="nav-item", style={"paddingLeft": "40px"}),
                            dbc.NavLink("Material Cards", href="/materials", active="exact", class_name="nav-item", style={"paddingLeft": "40px"}),
                            dbc.NavLink("Option Cards", href="/options", active="exact", class_name="nav-item", style={"paddingLeft": "40px"}),
                            dbc.NavLink("Universes", href="/universes", active="exact", class_name="nav-item", style={"paddingLeft": "40px"}),
                        ],
                    ),
                ], style={"backgroundColor": navbar_color, "border": "none"}
            )
        ],
        vertical=True,
        pills=True,
    )),

], style={
    'backgroundColor': navbar_color,
    'width': navbar_width,
    'height': '100vh',
    'position': 'fixed',
})

console = html.Div([
    dbc.Row([
        dbc.Col(html.Div("Console", style={'textAlign': 'left'}), width=3),
        dbc.Col(dcc.Input(id='file_path', type='text', placeholder='File path',
                          style={'textAlign': 'left'}, debounce=True), width='auto', style={'textAlign': 'right'}),
        dbc.Col(html.Button('Print File', id='print_button', n_clicks=0), width='auto', style={'marginRight': '6vw'}),
        dbc.Col(dcc.Checklist(id='element_comments', options=['Element Comments'], value=['Element Comments']),
                width='auto',
                style={'textAlign': 'left'}),
        dbc.Col(html.Div(html.Button("", id="console_toggler",
                                     className='minimize-button')), width='auto', style={'marginLeft': 'auto'})
    ], align='center',
        style={
            'marginTop': 20,
            'backgroundColor': 'black',
            'color': 'white',
            'padding': console_banner_height,
            'fontSize': 'calc((2vh + 1vw) / 2)',
        },
        className='gx-0'),

    dbc.Collapse(
        html.Div(
            id='console_output',
            style={
                'backgroundColor': '#333333',
                'color': '#A9A9A9',
                'border': '1px solid black',
                'borderBottom': 'none',
                'height': console_height,
                'overflow': 'scroll',
                'overflow-x': 'hidden',
            }, className='scrollbar-hidden'
        ),
        id='console_output_window',
        is_open=True
    )
],
    style={
        'marginLeft': navbar_width,
        'position': 'fixed',
        'bottom': 0,
        'width': f'calc(100% - {navbar_width})',
    }
)

content = html.Div(
    id="page_content",
    style={'marginLeft': navbar_width,
           'backgroundColor': page_background,
           'overflow': 'auto',
           'width': f'calc(100vw - {navbar_width})',
           'height': f'calc(100vh)',
           }
)

app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id='manually-closed', data=False),
    dbc.Row([
        dbc.Col(navbar, width='auto'),
        dbc.Col([
            content,
            html.Hr(),
            console
        ])
    ], justify="start", className="g-0")
], style={'overflow': 'hidden',  # prevent scrolling
          'height': '100vh',
          'width': '100vw',
          }
)


@app.callback(
    Output("card-views-collapse", "is_open"),
    [Input("card-views-toggle", "n_clicks")],
    [State("card-views-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('page_content', 'children'),
    Output('console_output_window', 'is_open', allow_duplicate=True),
    Input('url', 'pathname'),
    State('manually-closed', 'data'),
    prevent_initial_call=True,
)
def display_page(pathname, manually_closed):
    console_should_open = not manually_closed
    if pathname == '/':
        return home.layout(page_background), False
    elif pathname == '/cells':
        return cells.layout(page_background), console_should_open
    elif pathname == '/surfaces':
        return surfaces.layout(page_background), console_should_open
    elif pathname == '/materials':
        return materials.layout(page_background), console_should_open
    elif pathname == '/universes':
        return universes.layout(page_background), console_should_open
    elif pathname == '/assembly':
        return fuel_assemblies.layout(page_background), console_should_open
    elif pathname == '/plate':
        return plate.layout(page_background), console_should_open
    elif pathname == '/legacy_assembly':
        return legacy_fuel_assemblies.layout(page_background), console_should_open
    elif pathname == '/options':
        return options.layout(page_background), console_should_open
    else:
        return '404 Error: This page does not exist...YET!', False


@app.callback(
    Output('console_output_window', 'is_open', allow_duplicate=True),
    Output('manually-closed', 'data'),
    Input('console_toggler', 'n_clicks'),
    State('console_output_window', 'is_open'),
    State('manually-closed', 'data'),
    prevent_initial_call=True,
)
def toggle_console(n, is_open, manually_closed):
    if n:
        return not is_open, not manually_closed
    return is_open, False


@app.callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('print_button', 'n_clicks'),
    State('file_path', 'value'),
    State('element_comments', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def print_button(print_clicked, file_path, element_comments, current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'print_button':
        element_comments = element_comments != []
        printed = template.print_file(file_path, element_comments)
        message = f'({timestamp})\tPrinted the file to: {printed}'
        current_messages.insert(0, html.P(message))
    return current_messages


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':  # Only opens browser on start if main process
        Timer(1, open_browser).start()
    app.run_server(debug=True, threaded=True)
