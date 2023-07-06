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
                    dbc.Col('Current Cell:', width=3, align='end', className='current-card'),
                    dbc.Col(dcc.Dropdown(id='cell_selector', placeholder='Select a Cell', clearable=True,
                                         persistence=True, persistence_type='session',
                                         style={'width': '10vw', 'textAlign': 'left'}), width=3, align='center')
                ]),
                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        # Description
                        dbc.Row([
                            dbc.Col('Description:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='cell_description', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        # Material dropdown
                        dbc.Row([
                            dbc.Col('Material:', className='input-label', width=2),
                            dbc.Col(dcc.Dropdown(id='cell_material_selector', placeholder="", clearable=False,
                                                 style={'color': 'black'}), width=3),
                            dbc.Col(id='cell_material_description', children='Material Description',
                                    style={'textAlign': 'left', 'fontSize': 'calc(5px + 0.5vw)', 'color': 'black'}, width=7),
                        ], align='center', style={'marginTop': 20}),

                        # Density input
                        dbc.Row([
                            dbc.Col('Density:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='density_input', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        # Geometry input
                        dbc.Row([
                            dbc.Col('Geometry:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='geom_input', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        # Parameters input
                        dbc.Row([
                            dbc.Col('Parameters:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='param_input', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        html.Hr(),

                        html.Button('Apply Changes', id='cell_apply_button', n_clicks=0, className='apply-button')
                    ], width=6),

                    dbc.Col([
                        dcc.Tabs([
                            dcc.Tab(label='Print Preview',
                                    className='tab',
                                    children=dcc.Textarea(
                                        id='cell_preview',
                                        style={
                                            'fontSize': 'calc(5px + 0.5vw)',
                                            'backgroundColor': '#333333',
                                            'color': '#A9A9A9',
                                            'border': '3px solid black',
                                            'height': '60vh',
                                            'width': '40vw',
                                            'overflow': 'scrollX',
                                            'inputMode': 'email',
                                        }, className='scrollbar-hidden'
                                    )
                                    )
                        ], className='tab-container')
                    ], width=6)
                ]),
            ], fluid=True)])
    ]


@callback(
    Output('cell_material_selector', 'value'),
    Output('density_input', 'value'),
    Output('geom_input', 'value'),
    Output('param_input', 'value'),
    Output('cell_material_description', 'children'),
    Output('cell_description', 'value'),
    Output('cell_preview', 'value'),
    Input('cell_selector', 'value'),
    Input('cell_material_selector', 'value'),
)
def update_cell_display(cell, cell_material_select):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'cell_selector' or ctx.triggered_id is None:
        if cell is not None:
            selected_cell = template.all_cells.get(cell)
            return selected_cell.get_material(), selected_cell.get_density(), selected_cell.geom, selected_cell.param, template.all_materials.get(
                selected_cell.get_material()).comment, selected_cell.comment, str(selected_cell)
        else:
            return "", "", "", "", "Material Description", "", ""
    elif button_id == 'material_selector' and cell_material_select is not None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, template.all_materials.get(
            cell_material_select).comment, dash.no_update
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("cell_selector", "options"),
    Input("cell_selector", "search_value"),
)
def update_cell_options(search_value):
    return [o for o in template.all_cells]


@callback(
    Output("cell_material_selector", "options"),
    Input("cell_material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials]
    return result


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('cell_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('cell_selector', 'value'),
    State('cell_description', 'value'),
    State('cell_material_selector', 'value'),
    State('density_input', 'value'),
    State('geom_input', 'value'),
    State('param_input', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, cell, description, material, density, geom, param, current_messages):
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
            if selected_cell.comment == description and selected_cell.material == material and selected_cell.density == density and selected_cell.geom == geom and selected_cell.param == param:
                message = f'({timestamp})\tNo changes made to Cell {cell}'
                current_messages.insert(0, html.P(message))
                return current_messages

            if type(selected_cell) is RegularCell:
                if description is not None:
                    selected_cell.comment = description

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
                if selected_cell.comment == description and "Void" == material and "Void" == density and selected_cell.geom == geom and selected_cell.param == param:
                    message = f'({timestamp})\tNo changes made to Cell {cell}'
                    current_messages.insert(0, html.P(message))
                    return current_messages
                if material != "Void" or density != "Void":
                    message = f'({timestamp})\tCannot make changes to material or density of a void cell'
                    current_messages.insert(0, html.P(message))
                    return current_messages

                if description is not None:
                    selected_cell.comment = description

                if geom is not None:
                    selected_cell.geom = geom

                if param is not None:
                    selected_cell.param = param

                message = f'({timestamp})\tApplied changes to Void Cell {cell}'
                current_messages.insert(0, html.P(message))

        return current_messages
