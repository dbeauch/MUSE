import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

import Template_Editor.mcnp_cards
from Template_Editor.mcnp_cards import RegularCell, VoidCell, LikeCell
from Template_Editor.template_handler_instance import template_handler_instance as template


def layout(page_background):
    return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([
                    # Top spacing
                    dbc.Row([dbc.Col(html.H1(" "))]),

                    # Current Cell dropdown
                    dbc.Row([
                        dbc.Col(width=1),
                        dbc.Col(html.H4("Current Cell:"), width=3, align="end"),
                        dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Select a Cell', clearable=True, persistence=True, persistence_type='session', style={'width': '10vw'}), width=2,
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

                    dbc.Row([
                        dbc.Col(html.Button('Apply Changes', id='cell_apply_button', n_clicks=0), width=4),
                        dbc.Col(width=7),
                    ], className='g-0')
                ]),
            ])
        ]


@callback(
    Output('material_selector', 'value'),
    Output('density_input', 'value'),
    Output('geom_input', 'value'),
    Output('param_input', 'value'),
    Output('material_description', 'children'),
    Output('cell_description', 'children'),
    Input('cell_selector', 'value'),
    Input('material_selector', 'value'),
)
def update_cell_display(cell, material_select):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'cell_selector' or ctx.triggered_id is None:
        if cell is not None:
            selected_cell = template.all_cells.get(cell)
            return selected_cell.get_material(), selected_cell.get_density(), selected_cell.geom, selected_cell.param, template.all_materials.get(selected_cell.get_material()).comment, selected_cell.comment
        else:
            return "", "", "", "", "Material Description", "Cell Description"
    elif button_id == 'material_selector' and material_select is not None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, template.all_materials.get(material_select).comment, dash.no_update
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("cell_selector", "options"),
    Input("cell_selector", "search_value"),
)
def update_cell_options(search_value):
    return [o for o in template.all_cells]


@callback(
    Output("material_selector", "options"),
    Input("material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials]
    return result


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('cell_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('cell_selector', 'value'),
    State('material_selector', 'value'),
    State('density_input', 'value'),
    State('geom_input', 'value'),
    State('param_input', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, cell, material, density, geom, param, current_messages):
    if pathname == '/cells':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'cell_apply_button' and cell is not None:
            if material is None:
                return current_messages
            selected_cell = template.all_cells.get(cell)
            print(selected_cell.material)
            print(material)
            if selected_cell.material == material and selected_cell.density == density and selected_cell.geom == geom and selected_cell.param == param:
                message = f'({timestamp})\tNo changes made to Cell {cell}'
                current_messages.insert(0, html.P(message))
                return current_messages

            if type(selected_cell) is RegularCell:
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
                return current_messages
            elif type(selected_cell) is LikeCell:
                print("WIP Page change")
            elif type(selected_cell) is VoidCell:
                if "Void" == material and "Void" == density and selected_cell.geom == geom and selected_cell.param == param:
                    message = f'({timestamp})\tNo changes made to Cell {cell}'
                    current_messages.insert(0, html.P(message))
                    return current_messages
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

        return current_messages
    else:
        return
