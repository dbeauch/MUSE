import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(style={'backgroundColor': '#D3D3D3', 'height': '97vh'}, children=[
    html.Header("Py2MCNP Editor",
                style={'backgroundColor': 'green', 'color': 'white', 'padding': '20px', 'fontSize': '30px',
                       'textAlign': 'center'}),

    html.Div(style={'backgroundColor': 'black', 'height': '5px'}),

    dbc.Container([
        html.H4('Cell Changes', style={'textAlign': 'left'}),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Cell', style={'color': 'black'}), width=4),
            dbc.Col(dcc.Dropdown(id='material_selector', placeholder='Material', style={'color': 'black'}), width=4),
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
               'height': '200px', 'overflowY': 'scroll', 'marginTop': 350},
    ),
])


@app.callback(
    Output('console-output', 'children'),
    Input('apply_button', 'n_clicks'),
    Input('print_button', 'n_clicks'),
    State('cell_selector', 'value'),
    State('material_selector', 'value'),
    State('file_path', 'value'),
    State('console-output', 'children')
)
def update_output(apply_clicked, print_clicked, cell, material, file_path, current_messages):
    # Add your pre and post processing code here. The following is for demonstration purposes only.
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'apply_button':
        # Add the logic for applying changes here
        new_message = f'Applied changes: Cell {cell} Material {material}'

    elif button_id == 'print_button':
        # Add the logic for printing the file here
        new_message = f'Printed the file to: {file_path}'

    current_messages.append(new_message)

    # Convert messages to HTML p elements
    current_messages = [html.P(message) for message in current_messages]

    return current_messages


if __name__ == '__main__':
    app.run_server(debug=True)
