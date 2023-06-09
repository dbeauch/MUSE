import sys
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from template_handler import *

sys.setrecursionlimit(8000)
read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div(style={'backgroundColor': '#D3D3D3', 'height': '97vh'}, children=[
    html.Header("Py2MCNP Editor",
                style={'backgroundColor': 'green', 'color': 'white', 'padding': '20px', 'fontSize': '30px',
                       'textAlign': 'center'}),

    html.Div(style={'backgroundColor': 'black', 'height': '5px'}),

    dbc.Container([
        html.H4('Cell Changes', style={'textAlign': 'left'}),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Select a Cell'), width=4),
            dbc.Col(dcc.Dropdown(id='material_selector', placeholder='Select a Material', style={'color': 'black'}), width=4),
            dbc.Col(html.Button('Apply Changes', id='apply_button', n_clicks=0), width=4),
        ], style={'marginTop': 20}),

        html.Hr(),

        html.H4('Printing', style={'textAlign': 'left'}),
        dbc.Row([
            dbc.Col(dcc.Input(id='file_path', type='text', placeholder='File path', debounce=True), width=8),
            dbc.Col(html.Button('Print File', id='print_button', n_clicks=0), width=4),
        ], style={'marginTop': 20}),

    ], style={'marginTop': 20, 'marginBottom': 20}),

    html.Div(style={'backgroundColor': 'black', 'height': '5px'}),

    html.Div(
        id='console-output',
        style={'backgroundColor': '#333333', 'color': '#A9A9A9', 'margin-top': '20px', 'border': '1px solid black',
               'height': '200px', 'overflow': 'scroll', 'marginTop': 350},
    ),
])


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

    if button_id == 'apply_button':
        all_cells.get(cell).material = material
        message = f'Applied changes: Cell {cell} changed to Material {material}\n'
        current_messages.append(message)

    elif button_id == 'print_button':
        printed = print_file(file_path)
        message = f'Printed the file to: {printed}\n'
        current_messages.append(html.P(message))

    return current_messages


@app.callback(
    Output("cell_selector", "options"),
    Input("cell_selector", "search_value")
)
def update_cell_options(search_value):
    return [o for o in all_cells]


material_options = [1, 2, 3, 4, 'placeholders']


@app.callback(
    Output("material_selector", "options"),
    Input("material_selector", "search_value")
)
def update_cell_options(search_value):
    return [o for o in material_options]


if __name__ == '__main__':
    app.run_server(debug=True)
