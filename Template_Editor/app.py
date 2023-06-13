import sys
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from template_handler import *
import datetime

sys.setrecursionlimit(8000)
read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])

page_background = '#D3D3D3'
sidebar_color = '#993300'
sidebar_width = 300
console_height = 200

banner = html.Header("Py2MCNP Editor",
                     style={'backgroundColor': sidebar_color, 'color': 'white', 'padding': '0px', 'fontSize': '30px',
                            'textAlign': 'center'})
sidebar = html.Div([
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
], style={'color': 'black', 'backgroundColor': sidebar_color, 'width': sidebar_width, 'height': '100vh',
          'position': 'fixed'})

console = html.Div([
    dbc.Row([
        dbc.Col("Console", width=4, align='center'),
        dbc.Col(dcc.Input(id='file_path', type='text', placeholder='File path', debounce=True),
                width=1, align='center'),
        dbc.Col(html.Button('Print File', id='print_button', n_clicks=0), width=1, align='center'),
        dbc.Col(width=6),
    ], style={'marginTop': 20, 'backgroundColor': 'black', 'color': 'white', 'padding': '5px',
              'fontSize': '18px'}, className='g-0'),

    html.Div(id='console-output',
             style={'backgroundColor': '#333333', 'color': '#A9A9A9',
                    'border': '1px solid black',
                    'height': console_height, 'overflow': 'scroll'},
             )
], style={'marginLeft': sidebar_width, 'position': 'fixed', 'bottom': 0, 'width': 'calc(100%)'})

content = html.Div(id="page-content", style={'marginLeft': sidebar_width, 'backgroundColor': page_background})

app.layout = html.Div([dcc.Location(id="url"),
                       dbc.Row([
                           dbc.Col(sidebar, width='auto'),
                           dbc.Col([
                               content,
                               console
                           ])
                       ], justify="start", className="g-0")
                       ])


@app.callback(
    Output('console-output', 'children'),
    Input('apply_button', 'n_clicks'),
    Input('print_button', 'n_clicks'),
    State('cell_selector', 'value'),
    State('material_selector', 'value'),
    State('density_input', 'value'),
    State('geom_input', 'value'),
    State('param_input', 'value'),
    State('file_path', 'value'),
    State('console-output', 'children'),
    prevent_initial_call=True
)
def update_output(apply_clicked, print_clicked, cell, material, density, geom, param, file_path, current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'apply_button' and cell is not None:
        try:
            selected_cell = all_cells.get(cell)

            if material is not None:
                selected_cell.material = material

            if density is not None:
                selected_cell.density = density

            if geom is not None:
                selected_cell.geom = geom

            if param is not None:
                selected_cell.param = param

            message = f'({timestamp})\tApplied changes to Cell {cell}'
            current_messages.insert(0, html.P(message))
        except Exception as e:
            message = f'({timestamp})\tError applying changes: {str(e)}'
            current_messages.insert(0, html.P(message))

    if button_id == 'print_button':
        printed = print_file(file_path)
        message = f'({timestamp})\tPrinted the file to: {printed}'
        current_messages.insert(0, html.P(message))

    return current_messages


@app.callback(
    Output('material_selector', 'value'),
    Output('density_input', 'value'),
    Output('geom_input', 'value'),
    Output('param_input', 'value'),
    Output('material_description', 'children'),
    Input('cell_selector', 'value'),
    prevent_initial_call=True
)
def update_cell_info(cell):
    if cell is not None:
        selected_cell = all_cells.get(cell)
        return selected_cell.material, selected_cell.density, selected_cell.geom, selected_cell.param, f"Material {selected_cell.material} Description"
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


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
def update_material_options(search_value):
    return [o for o in all_materials]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return [
            html.Div([
                html.H1('Welcome to Py2MCNP Editor!'),
                html.P(
                    "This is a project designed to produce Monte Carlo N-Particle transport code (MCNP) card decks using Python"),
            ], style={'backgroundColor': page_background, 'height': '100vh', 'marginLeft': '20px'})
        ]

    elif pathname == "/cells":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([
                    # Top spacing
                    dbc.Row([dbc.Col(html.H1(" "))]),

                    # Current Cell dropdown
                    dbc.Row([
                        dbc.Col(width=4),
                        dbc.Col(html.H4("Current Cell:"), width=2, align="end"),
                        dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Select a Cell', clearable=True), width=2, align="center"),
                        dbc.Col(width=4),
                    ], justify="center"),

                    html.Hr(),

                    # Material dropdown
                    dbc.Row([
                        dbc.Col(html.H5("Material:    "), width='auto', align="end"),
                        dbc.Col(dcc.Dropdown(id='material_selector', placeholder='Select a Material Number', clearable=False, style={'color': 'black'}), width=3),
                        dbc.Col(html.H6(id='material_description', children='Material Description'), width=7)
                    ], justify="start", align="center"),

                    # Density input
                    html.H6("Density:", style={'marginTop': 20}),
                    dbc.Input(id='density_input', type='text', placeholder="Enter the density"),

                    # Geometry input
                    html.H6("Geometry:", style={'marginTop': 20}),
                    dbc.Input(id='geom_input', type='text', placeholder="Enter the geometry"),

                    # Parameters input
                    html.H6("Parameters:", style={'marginTop': 20}),
                    dbc.Input(id='param_input', type='text', placeholder="Enter the parameters"),

                    html.Hr(),

                    dbc.Col(html.Button('Apply Changes', id='apply_button', n_clicks=0), width=4),
                ]),
            ])
        ]

    elif pathname == "/surfaces":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([

                ])
            ])
        ]

    elif pathname == "/materials":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([

                ]),
            ])
        ]

    elif pathname == "/options":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([

                ]),
            ])
        ]

    # If the user tries to reach a different page, return a 404 message
    return html.P("Page not found")


if __name__ == '__main__':
    app.run_server(debug=True)
