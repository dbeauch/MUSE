import sys
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from template_handler import *

sys.setrecursionlimit(8000)
read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

banner = html.Header("Py2MCNP Editor",
                     style={'backgroundColor': 'green', 'color': 'white', 'padding': '0px', 'fontSize': '30px',
                            'textAlign': 'center'})

sidebar_width = '300px'
sidebar = html.Div([
    banner,
    dbc.Nav(
        [
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Edit Cells", href="/page-1", active="exact"),
        ],
        vertical=True,
        pills=True,
        style={'margin': '20px'},
    ),
], style={'backgroundColor': 'green', 'width': sidebar_width, 'height': '100vh', 'position': 'fixed'})

content = html.Div(id="page-content", style={'marginLeft': sidebar_width})

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(
    Output('console-output', 'children'),
    Input('apply_button', 'n_clicks'),
    Input('print_button', 'n_clicks'),
    State('cell_selector', 'value'),
    State('material_selector', 'value'),
    State('file_path', 'value'),
    State('console-output', 'children'),
    prevent_initial_call=True
)
def update_output(apply_clicked, print_clicked, cell, material, file_path, current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'apply_button' and cell is not None and material is not None:
        all_cells.get(cell).material = material
        message = f'Applied changes: Cell {cell} changed to Material {material}'
        current_messages.append(html.P(message))

    elif button_id == 'print_button':
        printed = print_file(file_path)
        message = f'Printed the file to: {printed}'
        current_messages.append(html.P(message))

    return current_messages


@app.callback(
    Output("cell_selector", "options"),
    Input("cell_selector", "search_value")
)
def update_cell_options(search_value):
    return [o for o in all_cells]


@app.callback(
    Output("material_selector", "options"),
    Input("material_selector", "search_value")
)
def update_cell_options(search_value):
    return [o for o in all_materials]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return [
            html.Div([
                html.H1('Welcome to Py2MCNP Editor!'),
                html.P("This is a project designed to produce Monte Carlo N-Particle transport code (MCNP) card decks using Python"),
            ], style={'marginLeft': '20px'})
        ]

    elif pathname == "/page-1":
        return [
            html.Div(style={'backgroundColor': '#D3D3D3', 'height': '100vh'}, children=[
                dbc.Container([
                    html.H4('Cell Changes', style={'textAlign': 'left'}),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Select a Cell Number', clearable=False), width=4),
                        dbc.Col(dcc.Dropdown(id='material_selector', placeholder='Select a Material Number', clearable=False,
                                             style={'color': 'black'}), width=4),
                        dbc.Col(html.Button('Apply Changes', id='apply_button', n_clicks=0), width=4),
                    ], style={'marginTop': 20}),

                    html.Hr(),

                    html.H4('Printing', style={'textAlign': 'left'}),
                    dbc.Row([
                        dbc.Col(dcc.Input(id='file_path', type='text', placeholder='File path', debounce=True),
                                width=8),
                        dbc.Col(html.Button('Print File', id='print_button', n_clicks=0), width=4),
                    ], style={'marginTop': 20}),

                ], style={'marginTop': 0, 'marginBottom': 0}),

                html.Div(style={'marginTop': 20, 'backgroundColor': 'black', 'height': '5px'}),

                html.Div(
                    id='console-output',
                    style={'backgroundColor': '#333333', 'color': '#A9A9A9', 'margin-top': '20px',
                           'border': '1px solid black',
                           'height': '200px', 'overflow': 'scroll', 'marginTop': 510},
                ),
            ])
        ]

    # If the user tries to reach a different page, return a 404 message
    return html.P("Page not found")


if __name__ == '__main__':
    app.run_server(debug=True)
