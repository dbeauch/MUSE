import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from Template_Editor.template_handler_instance import template_handler_instance as template


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
                                dbc.Button("Edit", id="section_open", color="primary", className='edit-modal'),
                                section_modal,
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        # Fuel Lattice row
                        dbc.Row([
                            dbc.Col('Fuel Lattice:', className='input-label', width=2),
                            dbc.Col(dbc.Input(id='lattice_number', className='input-box'), width=3),
                            dbc.Col([
                                dbc.Button("Edit", id="lattice_open", color="primary", className='edit-modal'),
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
                                dbc.Button("Edit", id="plate_open", color="primary", className='edit-modal'),
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
                                dbc.Button("Edit", id="component_open", color="primary", className='edit-modal'),
                                component_modal,
                            ], className='input-box'),
                        ], align='center', className='input-row'),

                        html.Hr(),

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
        result = [o for o in template.all_fuel_sections[assembly_u]]
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
            lat_universe = selected_assembly[0].fill[0]
            if selected_assembly[0] is not None:
                assembly_results = f'Fuel Section Cell:\n'
                assembly_results += f'\n'.join(str(card) for card in template.all_fuel_assemblies.get(assembly_u))
                assembly_results += f'\n\nFuel Lattice Cell:\n'
                assembly_results += f'{template.all_universes.get(template.all_fuel_assemblies.get(assembly_u)[0].fill[0])[0]}'
                assembly_results += f'\n\nOther Assembly Contents:\n'
                assembly_results += f'\n'.join(
                    str(card) for card in template.all_universes.get(assembly_u) if card.material != '0')

                # Not worth readability sacrifice to use list comprehension
                plate_preview = ""
                for plate_num in template.all_fuel_sections.get(assembly_u):
                    plate_preview += f'Plate Universe {plate_num}:\n'
                    for meat_cell in template.all_fuel_plates.get(plate_num):
                        plate_preview += str(meat_cell) + f'\n'
                    plate_preview += f'\n\n'

                return assembly_results, plate_preview, description_results, selected_assembly[0].number, \
                    template.all_universes.get(template.all_fuel_assemblies.get(assembly_u)[0].fill[0])[0].number
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('assembly_selector', 'value'),
    Input('assembly_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('assembly_selector', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, assembly, current_messages):
    if pathname == '/assembly':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # if button_id == 'assembly_apply_button' and assembly is not None:
        #     if something is None:
        #         return current_messages, dash.no_update
        #     selected_assembly = template.all_assembly.get(assembly)
        #     if selected_assembly == assembly:
        #         message = f'({timestamp})\tNo changes made to Assembly {assembly}'
        #         current_messages.insert(0, html.P(message))
        #         return current_messages, assembly
        #
        #     message = f'({timestamp})\tApplied changes to Assembly {assembly}'
        #     current_messages.insert(0, html.P(message))
        #     return current_messages, assembly

        return current_messages, dash.no_update


@callback(
    Output("section_modal", "is_open"),
    Input("section_open", "n_clicks"),
    Input("section_close", "n_clicks"),
    State("section_modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("lattice_modal", "is_open"),
    Input("lattice_open", "n_clicks"),
    Input("lattice_close", "n_clicks"),
    State("lattice_modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("plate_modal", "is_open"),
    Input("plate_open", "n_clicks"),
    Input("plate_close", "n_clicks"),
    State("plate_modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("component_modal", "is_open"),
    Input("component_open", "n_clicks"),
    Input("component_close", "n_clicks"),
    State("component_modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


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

section_modal = dbc.Modal(id="section_modal",
                          children=[dbc.ModalHeader("Edit Section Attributes"),
                                    dbc.ModalBody(
                                        [
                                            dbc.Label("Section Attributes:"),
                                            dcc.Dropdown(id='section_material__selector',
                                                         placeholder='Select a Section Attribute',
                                                         clearable=True,
                                                         persistence=True, persistence_type='session',
                                                         className='dropdown'),
                                            dbc.Label("New Value:"),
                                            dbc.Input(id="new_value_input", type="text",
                                                      placeholder="Enter new value")
                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="section_close", className="ml-auto")
                                    ),
                                    ],
                          is_open=False, modal_class_name='assembly-modal')

lattice_modal = dbc.Modal(id="lattice_modal",
                          children=[dbc.ModalHeader("Edit Lattice Attributes"),
                                    dbc.ModalBody(
                                        [
                                            dbc.Label("Lattice Attributes:"),
                                            dcc.Dropdown(id='lattice_material__selector',
                                                         placeholder='Select a Lattice Attribute',
                                                         clearable=True,
                                                         persistence=True, persistence_type='session',
                                                         className='dropdown'),
                                            dbc.Label("New Value:"),
                                            dbc.Input(id="new_value_input", type="text",
                                                      placeholder="Enter new value")
                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="lattice_close", className="ml-auto")
                                    ),
                                    ],
                          is_open=False, modal_class_name='assembly-modal')

plate_modal = dbc.Modal(id="plate_modal",
                        children=[dbc.ModalHeader("Edit Plate Attributes"),
                                  dbc.ModalBody(
                                      [
                                          dbc.Label("Material Attributes:"),
                                          dcc.Dropdown(id='plate_material__selector',
                                                       placeholder='Select a Material Attribute',
                                                       clearable=True,
                                                       persistence=True, persistence_type='session',
                                                       className='dropdown'),
                                          dbc.Label("New Value:"),
                                          dbc.Input(id="new_value_input", type="text",
                                                    placeholder="Enter new value")
                                      ]
                                  ),
                                  dbc.ModalFooter(
                                      dbc.Button("Close", id="plate_close", className="ml-auto")
                                  ),
                                  ],
                        is_open=False, modal_class_name='assembly-modal')

component_modal = dbc.Modal(id="component_modal",
                            children=[dbc.ModalHeader("Edit Component Attributes"),
                                      dbc.ModalBody(
                                          [
                                              dbc.Label("Component Attributes:"),
                                              dcc.Dropdown(id='component_material__selector',
                                                           placeholder='Select a Component Attribute',
                                                           clearable=True,
                                                           persistence=True, persistence_type='session',
                                                           className='dropdown'),
                                              dbc.Label("New Value:"),
                                              dbc.Input(id="new_value_input", type="text",
                                                        placeholder="Enter new value")
                                          ]
                                      ),
                                      dbc.ModalFooter(
                                          dbc.Button("Close", id="component_close", className="ml-auto")
                                      ),
                                      ],
                            is_open=False, modal_class_name='assembly-modal')
