import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from Template_Editor.controllers.template_handler_instance import template_handler_instance as template
# Workaround import since files in pages folder import classes as Template_Editor.mcnp_cards.<Class>
# do not compare correctly with mcnp_cards.<Class>
from Template_Editor.models.mcnp_cards import LikeCell
from Template_Editor.pages.assembly_modals import section_modal, lattice_modal, plate_modal, component_modal


def layout(page_background):
    return [
        html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
            dbc.Container([
                # Top spacing
                dbc.Row([dbc.Col(html.H1(" "))]),

                # Current Assembly dropdown
                dbc.Row([
                    dbc.Col("Current Assembly:", width=3, align="end", className='current-card'),
                    dbc.Col(dcc.Dropdown(id='assembly_selector', placeholder='Select an Assembly', clearable=True,
                                         persistence=True, persistence_type='session',
                                         className='dropdown'),
                            width=3, align="center"),
                    dbc.Col(html.H5(id='assembly_description', children='Assembly Description'),
                            width=6, align="end"),
                ]),

                html.Hr(),

                dbc.Row([
                    dbc.Col([  # input half of content
                        # Fuel Section row
                        dbc.Row([
                            dbc.Col('Fuel Section:', className='input-label', width=2),
                            dbc.Col(dbc.Input(id='section_number', className='input-box'), width=3),
                            dbc.Col([
                                dbc.Button("Edit", id="section_open", color="primary", className='edit-modal-button'),
                                section_modal,
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        # Fuel Lattice row
                        dbc.Row([
                            dbc.Col('Fuel Lattice:', className='input-label', width=2),
                            dbc.Col(dbc.Input(id='lattice_number', className='input-box'), width=3),
                            dbc.Col([
                                dbc.Button("Edit", id="lattice_open", color="primary", className='edit-modal-button'),
                                lattice_modal,
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        # Plate row
                        dbc.Row([
                            dbc.Col('Plate:', className='input-label', width=2),
                            dbc.Col([dcc.Dropdown(id='plate_selector', placeholder='Select a Plate', clearable=True,
                                                  persistence=True, persistence_type='session', className='dropdown'
                                                  )], className='input-box', width=3),
                            dbc.Col([
                                dbc.Button("Edit", id="plate_open", color="primary", className='edit-modal-button'),
                                plate_modal,
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        # Other Components row
                        dbc.Row([
                            dbc.Col('Other Component:', className='input-label', width=2),
                            dbc.Col(
                                [dcc.Dropdown(id='component_selector', placeholder='Select a Component', clearable=True,
                                              persistence=True, persistence_type='session', className='dropdown'
                                              )], className='input-box', width=3),
                            dbc.Col([
                                dbc.Button("Edit", id="component_open", color="primary", className='edit-modal-button'),
                                component_modal,
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        # Master row
                        dbc.Row([
                            dbc.Col('Material:', className='input-label', width=2),
                            dbc.Col([dcc.Dropdown(id='master_material_selector', placeholder='Select a Material',
                                                  clearable=True,
                                                  persistence=True, persistence_type='session', className='dropdown'
                                                  )], className='input-box', width=3),
                            dbc.Col([
                                dbc.Button("Change All Fuel", id="master_button", color="primary",
                                           style={
                                               'width': 'calc(40px + 8vw)',
                                               'height': 'calc(10px + 2vh)',
                                               'fontSize': 'calc(1px + 0.4vw + 0.4vh)',
                                               'display': 'flex',
                                               'alignItems': 'center',
                                               'justifyContent': 'center'}),
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        # html.Button('Apply Changes', id='assembly_apply_button', n_clicks=0,
                        #             className='apply-button'),
                    ], width=6),

                    dbc.Col([
                        assembly_tabs
                    ], width=6)
                ]),
            ], fluid=True),
        ])
    ]


@callback(
    Output("plate_selector", "options"),
    Input("plate_selector", "search_value"),
    Input("assembly_selector", "value"),
)
def update_plate_options(search_value, assembly_u):
    if assembly_u is not None:
        result = [o for o in template.all_fuel_assemblies.get(assembly_u).plates]
        result.append("All Plates")
        result.sort()
        return result
    return dash.no_update


@callback(
    Output("assembly_selector", "options"),
    Input("assembly_selector", "search_value"),
)
def update_assembly_options(search_value):
    result = [o for o in template.all_fuel_assemblies.keys()]
    result.sort()
    return result


@callback(
    Output("master_material_selector", "options"),
    Input("master_material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials]
    result.sort()
    return result


@callback(
    Output('assembly_preview', 'value'),
    Output('plate_preview', 'value'),
    Output('assembly_description', 'children'),
    Output('section_number', 'value'),
    Output('lattice_number', 'value'),
    Input('assembly_selector', 'value'),
    Input('assembly_description', 'value'),
)
def update_assembly_display(assembly_u, descr):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'assembly_selector' or ctx.triggered_id is None:
        if assembly_u is not None:
            description_results = ""
            if assembly_u in template.data_comments.keys():
                description_results = template.data_comments.get(assembly_u)

            selected_assembly = template.all_fuel_assemblies.get(assembly_u)
            lat_universe = selected_assembly.fuel_lattice.universe
            if selected_assembly is not None:
                assembly_results = f'Fuel Section Cell:\n'
                assembly_results += f'{template.all_fuel_assemblies.get(assembly_u).fuel_section}'
                assembly_results += f'\n\nFuel Lattice Cell:\n'
                assembly_results += f'{template.all_fuel_assemblies.get(assembly_u).fuel_lattice}'
                assembly_results += f'\n\nOther Assembly Contents:\n'
                assembly_results += f'\n'.join(
                    str(card) for card in template.all_universes.get(assembly_u) if
                    card.material != '0')  # TODO: append components to Assembly

                # Not worth readability sacrifice to use list comprehension
                plate_preview = ""
                for plate_num in template.all_fuel_assemblies.get(assembly_u).plates:
                    plate_preview += f'Plate Universe {plate_num}:\n'
                    for meat_cell in template.all_fuel_plates.get(plate_num):
                        plate_preview += str(meat_cell) + f'\n'
                    plate_preview += f'\n\n'

                return assembly_results, plate_preview, description_results, selected_assembly.number, \
                    selected_assembly.fuel_lattice.number
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('master_button', 'n_clicks'),
    State('master_material_selector', 'value'),
    State('assembly_description', 'value'),
    State('url', 'pathname'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, new_mat, descr, pathname, current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'master_button' and new_mat is not None:
        if descr is None:
            return current_messages
        if template.all_materials.get(new_mat) is None:
            message = f'({timestamp})\tError: Material not found'
            current_messages.insert(0, html.P(message))
            return current_messages
        for assembly in template.all_fuel_assemblies.values():
            for plate in assembly.plates:
                for sect in template.all_fuel_plates.get(plate):
                    sect.material = new_mat
                    if type(sect) is LikeCell:
                        template.dissect_like_param(sect)
        message = f'({timestamp})\tApplied changes made to all plate sections'
        current_messages.insert(0, html.P(message))
        return current_messages
    return current_messages


assembly_tabs = dcc.Tabs([
    dcc.Tab(label='Assembly Preview',
            className='tab',
            children=dcc.Textarea(
                id='assembly_preview',
                style={
                    'fontSize': 'calc(5px + 0.5vw)',
                    'backgroundColor': '#333333',
                    'color': '#A9A9A9',
                    'border': '3px solid black',
                    'height': '60vh',
                    'width': '40vw',
                    'overflow': 'scrollX',
                    'inputMode': 'email',
                },
            )
            ),
    dcc.Tab(label='Plate Preview',
            className='tab',
            children=dcc.Textarea(
                id='plate_preview',
                style={
                    'fontSize': 'calc(5px + 0.5vw)',
                    'backgroundColor': '#333333',
                    'color': '#A9A9A9',
                    'border': '3px solid black',
                    'height': '60vh',
                    'width': '40vw',
                    'overflow': 'scrollX',
                    'inputMode': 'email',
                },
            )
            ),
], className='tab-container')
