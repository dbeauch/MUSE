import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import numpy as np

from Template_Editor.controllers.template_handler_instance import template_handler_instance as template
# Workaround import since files in pages folder import classes as Template_Editor.mcnp_cards.<Class>
# do not compare correctly with mcnp_cards.<Class>
from Template_Editor.models.mcnp_cards import LikeCell
from Template_Editor.pages.select_graphs import assembly_graph, plate_graph, segment_graph


def layout(page_background):
    return [
        html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
            dbc.Container([
                # Top spacing
                dbc.Row([dbc.Col(html.H1(" "))]),

                # Current Assembly dropdown
                dbc.Row([
                    dbc.Col(html.H5(id='assembly_description', children=''),
                            width=6, align="end"),
                    dbc.Col("View Assembly:", width=3, align="end", className='current-card'),
                    dbc.Col(dcc.Dropdown(id='assembly_selector', placeholder='Select an Assembly', clearable=True,
                                         persistence=True, persistence_type='session',
                                         className='dropdown'),
                            width=3, align="center"),
                ]),

                html.Hr(),

                dbc.Row([
                    dbc.Col([  # input half of content
                        dbc.Row([
                            dbc.Col([  # Plot Options
                                html.Div([
                                    dbc.Row("Select Options", className='input-label'),
                                    dbc.Row(dcc.RadioItems(
                                        id="select_mode",
                                        options=[
                                            {"label": "Single Select Mode", "value": "single"},
                                            {"label": "Multiselect Mode", "value": "multi"},
                                            {"label": "Unselect Mode", "value": "unselect"}
                                        ],
                                        value="single"  # Single by default
                                    )),
                                    dbc.Row("Mass Highlight Options", className='input-label'),
                                    dbc.Row(dbc.Switch(id="select_all_assemblies", label="All Assemblies", value=False)),
                                    dbc.Row(dbc.Switch(id="select_all_plates", label="All Plates", value=False)),
                                    dbc.Row(dbc.Switch(id="select_all_sections", label="All Sections", value=False))
                                ], className='plot-options'),
                                dbc.Row(dbc.Button("Unselect All", id='unselect_all_button', className='unselect-button')),
                            ], width=4),

                            dbc.Col([   # Plot Tabs
                                dcc.Tabs([
                                    dcc.Tab(label='Assembly Plot',
                                            className='tab',
                                            children=assembly_graph
                                            ),
                                    dcc.Tab(label='Plates Plot',
                                            className='tab',
                                            children=plate_graph
                                            ),
                                    dcc.Tab(label='Segments Plot',
                                            className='tab',
                                            children=segment_graph
                                            ),
                                ], className='tab-container')
                            ], width=8),
                        ]),
                        dbc.Row([
                            # Edit Options
                        ])
                    ]),

                    dbc.Col([
                        assembly_tabs
                    ], width=6)
                ]),
            ], fluid=True),
        ])
    ]


@callback(
    Output("assembly_selector", "options"),
    Input("assembly_selector", "search_value"),
)
def update_assembly_options(search_value):
    result = [o for o in template.all_fuel_assemblies.keys()]
    result.sort()
    return result


@callback(
    Output("select_all_plates", "value"),
    Output("select_all_sections", "value", allow_duplicate=True),
    Input("select_all_assemblies", "value"),
    prevent_initial_call=True
)
def update_from_assemblies(select_all_assemblies):
    # If "Select All Assemblies" is toggled on (i.e., its value is True),
    # set the value of "Select All Plates" and "Select All Sections" to True.
    # If "Select All Assemblies" is toggled off (i.e., its value is False),
    # do nothing to the other switches.
    if select_all_assemblies:
        return True, True
    return dash.no_update, dash.no_update


@callback(
    Output("select_all_sections", "value", allow_duplicate=True),
    Input("select_all_plates", "value"),
    prevent_initial_call=True
)
def update_from_plates(select_all_plates):
    # If "Select All Plates" is toggled on (i.e., its value is True),
    # set the value of "Select All Sections" to True.
    # If "Select All Plates" is toggled off (i.e., its value is False),
    # do nothing to the other switch.
    if select_all_plates:
        return True
    return dash.no_update


@callback(
    Output("select_all_assemblies", "value", allow_duplicate=True),
    Output("select_all_plates", "value", allow_duplicate=True),
    Output("select_all_sections", "value", allow_duplicate=True),
    Input("unselect_all_button", "n_clicks"),
    prevent_initial_call=True
)
def unselect_all(n_clicks):
    # When the "Unselect All" button is clicked,
    # set the value of all switches to False.
    if n_clicks:
        return False, False, False
    return dash.no_update, dash.no_update, dash.no_update


@callback(
    Output('assembly_preview', 'value'),
    Output('plate_preview', 'value'),
    Output('assembly_description', 'value', allow_duplicate=True),
    Input('assembly_selector', 'value'),
    Input('assembly_description', 'value'),
    prevent_initial_call=True
)
def update_assembly_display(assembly_u, descr):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id in ['assembly_selector', 'assembly_description'] or ctx.triggered_id is None:
        if assembly_u is not None:
            description_results = ""
            if assembly_u in template.data_comments.keys():
                description_results = template.data_comments.get(assembly_u)

            selected_assembly = template.all_fuel_assemblies.get(assembly_u)
            lat_universe = selected_assembly.fuel_lattice.universe
            if selected_assembly is not None:
                assembly_results = f'Fuel Section Cell:\n'
                assembly_results += f'{selected_assembly.fuel_section}'
                assembly_results += f'\n\nFuel Lattice Cell:\n'
                assembly_results += f'{selected_assembly.fuel_lattice}'
                assembly_results += f'\n\nOther Assembly Contents:\n'
                assembly_results += f'\n'.join(str(card) for card in selected_assembly.other_components)

                # Not worth readability sacrifice to use list comprehension
                plate_preview = ""
                for plate_num in selected_assembly.plates:
                    plate_preview += f'Plate Universe {plate_num}:\n'
                    for meat_cell in template.all_fuel_plates.get(plate_num):
                        plate_preview += str(meat_cell) + f'\n'
                    plate_preview += f'\n\n'

                return assembly_results, plate_preview, description_results
    return dash.no_update, dash.no_update, dash.no_update


#
# @callback(
#     Output('console_output', 'children', allow_duplicate=True),
#     Output('assembly_description', 'value', allow_duplicate=True),
#     State('assembly_description', 'value'),
#     State('url', 'pathname'),
#     State('console_output', 'children'),
#     prevent_initial_call=True
# )
# def update_console(descr, pathname, current_messages):
#     if not current_messages:
#         current_messages = []
#
#     ctx = dash.callback_context
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     timestamp = datetime.datetime.now().strftime("%H:%M:%S")
#
#     # if button_id == 'master_button' and new_mat is not None:
#     #     if descr is None:
#     #         return current_messages, descr
#     #     if template.all_materials.get(new_mat) is None:
#     #         message = f'({timestamp})\tError: Material not found'
#     #         current_messages.insert(0, html.P(message))
#     #         return current_messages, descr
#     #     for assembly in template.all_fuel_assemblies.values():
#     #         for plate in assembly.plates:
#     #             for sect in template.all_fuel_plates.get(plate):
#     #                 sect.material = new_mat
#     #                 if type(sect) is LikeCell:
#     #                     template.dissect_like_param(sect)
#     #     message = f'({timestamp})\tApplied changes made to all plate sections'
#     #     current_messages.insert(0, html.P(message))
#     #     return current_messages, descr
#     return current_messages, descr


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
