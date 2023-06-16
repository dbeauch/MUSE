import sys
import datetime

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from template_handler import *

# Sizes and Colors
navbar_width = '15vw'
console_height = '20vh'
console_banner_height = '0.2vh'
page_background = '#D3D3D3'
navbar_color = '#993300'

sys.setrecursionlimit(8000)
template = TemplateHandler()
template.read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')

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

console_toggler = html.Button("-", id="console-toggler")

console = html.Div([
    dbc.Row([
        dbc.Col("Console", width=4, align='center'),
        dbc.Col(
            dcc.Input(id='file_path', type='text', placeholder='File path', debounce=True),
            width=1, align='center'
        ),
        dbc.Col(html.Button('Print File', id='print_button', n_clicks=0), width=1, align='center'),
        dbc.Col(width=4),
        dbc.Col(console_toggler, width=2)
    ],
        style={
            'marginTop': 20,
            'backgroundColor': 'black',
            'color': 'white',
            'padding': console_banner_height,
            'fontSize': '18px'
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
    })

content = html.Div(
    id="page-content",
    style={'marginLeft': navbar_width, 'backgroundColor': page_background}
)

app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(navbar, width='auto'),
        dbc.Col([
            content,
            console
        ])
    ], justify="start", className="g-0")
])


@app.callback(
    Output('console_output', 'children'),
    Input('apply_button', 'n_clicks'),
    Input('print_button', 'n_clicks'),
    State('cell_selector', 'value'),
    State('material_selector', 'value'),
    State('density_input', 'value'),
    State('geom_input', 'value'),
    State('param_input', 'value'),
    State('file_path', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, print_clicked, cell, material, density, geom, param, file_path, current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'apply_button' and cell is not None:        # must use type() to filter Cell from LikeCell(Cell)
        selected_cell = template.all_cells.get(cell)
        if selected_cell.material == material and selected_cell.density == density and selected_cell.geom == geom and selected_cell.param == param:
            message = f'({timestamp})\tNo changes made to Cell {cell}'
            current_messages.insert(0, html.P(message))
            return current_messages

        if type(selected_cell) is Cell:
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
        elif type(selected_cell) is LikeCell:
            print("WIP Page change")
        elif type(selected_cell) is VoidCell:
            if material != "Void" or density != "Void":
                message = f'({timestamp})\tCannot make changes to material or density of a void cell'
                current_messages.insert(0, html.P(message))
                return current_messages

            if geom is not None:
                selected_cell.geom = geom

            if param is not None:
                selected_cell.param = param

            message = f'({timestamp})\tApplied changes to Void Cell {cell}'
            current_messages.insert(0, html.P(message))

    if button_id == 'print_button':
        printed = template.print_file(file_path)
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
    Input('material_selector', 'value'),
    prevent_initial_call=True
)
def update_cell_display(cell, material_select):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'cell_selector':
        if cell is not None:
            selected_cell = template.all_cells.get(cell)
            return selected_cell.get_material(), selected_cell.get_density(), selected_cell.geom, selected_cell.param, f"Material {selected_cell.get_material()} Description"
        else:
            return "", "", "", "", "Material Description"  # dash.no_update
    elif button_id == 'material_selector':
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"Material {material_select} Description"


@app.callback(
    Output("cell_selector", "options"),
    Input("cell_selector", "search_value")
)
def update_cell_options(search_value):
    return [o for o in template.all_cells]


@app.callback(
    Output("material_selector", "options"),
    Input("material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials.keys()]
    result.append("Void")
    result.append("WIP")
    return result


@app.callback(
    Output("console_output_window", "is_open", allow_duplicate=True),
    Input("console-toggler", "n_clicks"),
    State("console_output_window", "is_open"),
    prevent_initial_call=True,
)
def toggle_console(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("page-content", "children"),
    Output("console_output_window", "is_open", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True
)
def render_page_content(pathname):
    if pathname == "/":
        return [
            html.Div([
                html.H1('Welcome to Py2MCNP Editor!'),
                html.P(
                    "This is a project designed to produce Monte Carlo N-Particle transport code (MCNP) card decks "
                    "using Python"),
            ], style={'backgroundColor': page_background, 'height': '100vh', 'marginLeft': '20px'})
        ], False

    elif pathname == "/cells":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([
                    # Top spacing
                    dbc.Row([dbc.Col(html.H1(" "))]),

                    # Current Cell dropdown
                    dbc.Row([
                        dbc.Col(width=2),
                        dbc.Col(html.H4("Current Cell:"), width=2, align="end"),
                        dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Select a Cell', clearable=True), width=2,
                                align="center"),
                        dbc.Col(html.H5(id='cell_description', children='Cell Description'), width=6, align="end"),
                    ], justify="center"),

                    html.Hr(),

                    # Material dropdown
                    dbc.Row([
                        dbc.Col(html.H5("Material: "), width='auto', align="end"),
                        dbc.Col(dcc.Dropdown(id='material_selector', placeholder='', clearable=False,
                                             style={'color': 'black'}), width=3),
                        dbc.Col(html.H6(id='material_description', children='Material Description'), width=7)
                    ], justify="start", align="center"),

                    # Density input
                    html.H6("Density:", style={'marginTop': 20}),
                    dbc.Input(id='density_input', type='text', placeholder=""),

                    # Geometry input
                    html.H6("Geometry:", style={'marginTop': 20}),
                    dbc.Input(id='geom_input', type='text', placeholder=""),

                    # Parameters input
                    html.H6("Parameters:", style={'marginTop': 20}),
                    dbc.Input(id='param_input', type='text', placeholder=""),

                    html.Hr(),

                    dbc.Col(html.Button('Apply Changes', id='apply_button', n_clicks=0), width=4),
                ]),
            ])
        ], True

    elif pathname == "/surfaces":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([

                ])
            ])
        ], True

    elif pathname == "/materials":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([

                ]),
            ])
        ], True

    elif pathname == "/options":
        return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([

                ]),
            ])
        ], True
    return html.P("Page not found")


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
