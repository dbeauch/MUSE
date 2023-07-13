import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from Template_Editor.template_handler_instance import template_handler_instance as template
# Workaround import since files in pages folder import classes as Template_Editor.mcnp_cards.<Class>
# do not compare correctly with mcnp_cards.<Class>
from Template_Editor.template_handler_instance import RegularCell, VoidCell, LikeCell


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
                                         className='dropdown'),
                            width=3, align='center')
                ]),
                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        # Description
                        dbc.Row([
                            dbc.Col('Description:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='cell_description', type='text', className='input-box'))
                        ], align='center', className='input-row'),

                        # Material dropdown
                        dbc.Row([
                            dbc.Col('Material:', className='input-label', width=2),
                            dbc.Col(dcc.Dropdown(id='cell_material_selector', placeholder="", clearable=False,
                                                 className='dropdown'), width=3),
                            dbc.Col(id='cell_material_description', children='Material Description',
                                    style={'textAlign': 'left', 'fontSize': 'calc(5px + 0.5vw)', 'color': 'black'},
                                    width=7),
                        ], align='center', className='input-row'),

                        # Density input
                        dbc.Row([
                            dbc.Col('Density:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='density_input', type='text', className='input-box'))
                        ], align='center', className='input-row'),

                        # Geometry input
                        dbc.Row([
                            dbc.Col('Geometry:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='geom_input', type='text', className='input-box'))
                        ], align='center', className='input-row'),

                        # Parameters input
                        dbc.Row([
                            dbc.Col('Parameters:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='param_input', type='text', className='input-box'))
                        ], align='center', className='input-row'),

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
                                    ),
                            dcc.Tab(label='Related Cells',
                                    className='tab',
                                    children=dcc.Textarea(
                                        id='origin_preview',
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
    Output('origin_preview', 'value'),
    Input('cell_selector', 'value'),
    Input('cell_material_selector', 'value'),
)
def update_cell_display(cell, cell_material_select):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'cell_selector' or ctx.triggered_id is None:
        if cell is not None:
            selected_cell = template.all_cells.get(cell)
            if type(selected_cell) is LikeCell:
                second_tab = template.all_cells.get(selected_cell.origin_cell)
            elif type(selected_cell) in [RegularCell, VoidCell]:
                second_tab = "\n".join(str(o) for o in selected_cell.children)
            else:
                second_tab = f"Error: Generic Cell created: {selected_cell}"
            return selected_cell.get_material(), selected_cell.get_density(), selected_cell.geom, selected_cell.param, \
                template.all_materials.get(selected_cell.get_material()).comment, selected_cell.comment,\
                str(selected_cell), str(second_tab)
        else:
            return "", "", "", "", "Material Description", "", "", ""
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


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
    result.sort()
    return result


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('cell_selector', 'value'),
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
                return current_messages, dash.no_update
            selected_cell = template.all_cells.get(cell)
            if selected_cell.comment == description and selected_cell.material == material and \
                    selected_cell.density == density and selected_cell.geom == geom and selected_cell.param == param:
                message = f'({timestamp})\tNo changes made to Cell {cell}'
                current_messages.insert(0, html.P(message))
                return current_messages, dash.no_update

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

                # Propogate changes to children
                if len(selected_cell.children) > 0:
                    template.set_like_cell(selected_cell.children)

                message = f'({timestamp})\tApplied changes to Cell {cell}'
                current_messages.insert(0, html.P(message))
                return current_messages, cell

            elif type(selected_cell) is LikeCell:
                if description is not None:
                    selected_cell.comment = description

                if material is not None:
                    selected_cell.material = material
                    selected_cell.changes += f'mat={material}'
                    template.dissect_like_param(selected_cell)

                if density != selected_cell.density:
                    message = f'({timestamp})\tCannot make changes to density of a Like Cell'
                    current_messages.insert(0, html.P(message))
                    return current_messages, dash.no_update

                if geom != selected_cell.geom:
                    message = f'({timestamp})\tCannot make changes to geometry of a Like Cell'
                    current_messages.insert(0, html.P(message))
                    return current_messages, dash.no_update

                if param is not None:
                    selected_cell.param = param
                    template.dissect_like_param(selected_cell)

                message = f'({timestamp})\tApplied changes to Cell {cell}'
                current_messages.insert(0, html.P(message))
                return current_messages, cell

            elif type(selected_cell) is VoidCell:
                if selected_cell.comment == description and "Void" == material and "Void" == density \
                        and selected_cell.geom == geom and selected_cell.param == param:
                    message = f'({timestamp})\tNo changes made to Cell {cell}'
                    current_messages.insert(0, html.P(message))
                    return current_messages, dash.no_update
                if material != "0" or density != "Void":
                    message = f'({timestamp})\tCannot make changes to material or density of a Void Cell'
                    current_messages.insert(0, html.P(message))
                    return current_messages, dash.no_update

                if description is not None:
                    selected_cell.comment = description

                if geom is not None:
                    selected_cell.geom = geom

                if param is not None:
                    selected_cell.param = param

                message = f'({timestamp})\tApplied changes to Void Cell {cell}'
                current_messages.insert(0, html.P(message))
                return current_messages, cell

        return current_messages, dash.no_update
