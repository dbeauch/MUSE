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
        result = [o for o in template.all_fuel_sections[assembly_u]]
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
            # TODO: A lot of changes once assembly class
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
        for assembly in template.all_fuel_sections.keys():
            for plate in template.all_fuel_sections.get(assembly):
                print(plate)
                print(template.all_fuel_plates.get(plate))
                for sect in template.all_fuel_plates.get(plate):
                    print(sect)
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


section_modal = dbc.Modal(id="section_modal",
                          children=[dbc.ModalHeader("Edit Section Attributes"),
                                    dbc.ModalBody(
                                        [
                                            dbc.Label("Section Attributes:"),
                                            dcc.Dropdown(id='section_material_selector',
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


lattice_modal = dbc.Modal(id="lattice_modal",
                          children=[dbc.ModalHeader("Edit Lattice Attributes"),
                                    dbc.ModalBody(
                                        [
                                            dbc.Label("Lattice Attributes:"),
                                            dcc.Dropdown(id='lattice_material_selector',
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
    Output("plate_cell_selector", "options"),
    Output("plate_cell_selector", "value"),
    Input("plate_open", "n_clicks"),
    State("assembly_selector", "value"),
    State("plate_selector", "value"),
)
def modal_display(plate_button, assembly_u, plate_u):
    if assembly_u is not None and plate_u is not None:
        if plate_u == "All Plates":
            plate_options = ["All Sections"]
        else:
            plate_options = [o.number for o in template.all_fuel_plates[plate_u]]
        plate_options.sort()

        return plate_options, plate_options[0]
    return [], ""


@callback(
    Output("current_material", "value"),
    Input("plate_cell_selector", "value"),
    State("plate_selector", "value"),
)
def update_material(section_cell, plate_u):
    if plate_u is not None:
        if plate_u == "All Plates":
            return "Many"
        else:
            if section_cell is not None:
                for section in template.all_fuel_plates[plate_u]:
                    if section.number == section_cell:
                        return section.material
    return ""


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('assembly_description', 'value', allow_duplicate=True),
    Input("plate_apply", "n_clicks"),
    State('assembly_selector', 'value'),
    State('assembly_description', 'value'),
    State("plate_selector", "value"),
    State("plate_cell_selector", "value"),
    State("current_material", "value"),
    State("new_material", "value"),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def plate_apply_changes(plate_apply_button, assembly_u, descr, plate_u, section_cell, curr_mat, new_mat,
                        current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'plate_apply' and None not in [plate_u, section_cell, curr_mat, new_mat]:
        if template.all_materials.get(new_mat) is None:
            message = f'({timestamp})\tError: Material not found'
            current_messages.insert(0, html.P(message))
            return current_messages, ""
        if plate_u == "All Plates":
            for plate in template.all_fuel_sections.get(assembly_u):
                for sect in template.all_fuel_plates.get(plate):
                    sect.material = new_mat
                    if type(sect) is LikeCell:
                        template.dissect_like_param(sect)
            message = f'({timestamp})\tApplied changes made to all plate sections'
            current_messages.insert(0, html.P(message))
            return current_messages, ""
        else:
            if section_cell == "All Sections":
                pass
            else:
                selected_cell = None
                # Search for section TODO: change with Assembly class
                for section in template.all_fuel_plates[plate_u]:
                    if section.number == section_cell:
                        selected_cell = section

                if selected_cell is None:
                    message = f'({timestamp})\tError: Section not found'
                    current_messages.insert(0, html.P(message))
                    return current_messages, ""
                selected_cell.material = new_mat
                template.dissect_like_param(selected_cell)
                message = f'({timestamp})\tApplied changes made to Cell {selected_cell.number}'
                current_messages.insert(0, html.P(message))
                return current_messages, ""
    return current_messages, ""


plate_modal = dbc.Modal(id="plate_modal",
                        children=[dbc.ModalHeader("Edit Plate Attributes"),
                                  dbc.ModalBody(
                                      [
                                          dbc.Label("Section:"),
                                          dcc.Dropdown(id='plate_cell_selector',
                                                       placeholder='Select a Plate',
                                                       clearable=True,
                                                       persistence=True, persistence_type='session',
                                                       className='dropdown'),
                                          dbc.Row([
                                              dbc.Col([
                                                  dbc.Label("Current Material:"),
                                                  dbc.Input(id="current_material", type="text",
                                                            placeholder="Enter new value")
                                              ]),
                                              dbc.Col([
                                                  dbc.Label("New Material:"),
                                                  dbc.Input(id="new_material", type="text",
                                                            placeholder="Enter new value")
                                              ])
                                          ])
                                      ]
                                  ),
                                  dbc.ModalFooter([
                                      dbc.Button("Apply Changes", id="plate_apply", className="ml-auto"),
                                      dbc.Button("Close", id="plate_close", className="ml-auto")
                                  ]),
                                  ],
                        is_open=False, modal_class_name='assembly-modal')


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


component_modal = dbc.Modal(id="component_modal",
                            children=[dbc.ModalHeader("Edit Component Attributes"),
                                      dbc.ModalBody(
                                          [
                                              dbc.Label("Component Attributes:"),
                                              dcc.Dropdown(id='component_material_selector',
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
                            is_open=False, modal_class_name='assembly-modal', backdrop=False)
