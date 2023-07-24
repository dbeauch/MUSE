import datetime
from collections import OrderedDict

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
from Template_Editor.pages.select_graphs import selected_color, default_color, assembly_translator


def layout(page_background):
    return [
        html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
            dbc.Container([
                # Top spacing
                dbc.Row([dbc.Col(html.H1(" "))]),

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
                                    dbc.Row("Mass Highlight Options", className='input-label', style={'marginTop': '2vh'}),
                                    dbc.Button("All Assemblies", id='select_all_assemblies', className='unselect-button'),
                                    dbc.Button("All Plates", id='select_all_plates', className='unselect-button'),
                                    dbc.Button("All Sections", id='select_all_sections', className='unselect-button'),
                                    dbc.Button("Unselect All", id='unselect_all_button',className='unselect-button')
                                ], className='plot-options'),
                            ], width=4),

                            dcc.Store(id='assembly_plot_camera', storage_type='session'),
                            dcc.Store(id='plate_plot_camera', storage_type='session'),
                            dcc.Store(id='section_plot_camera', storage_type='session'),

                            dcc.Store(id='assembly_plot_selected', data=[], storage_type='session'),
                            dcc.Store(id='plate_plot_selected', data=[], storage_type='session'),
                            dcc.Store(id='section_plot_selected', data=[], storage_type='session'),

                            dbc.Col([  # Plot Tabs
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

                        html.Hr(),

                        dbc.Row([
                            dbc.Col('Assemblies:', className='input-label', width=2),
                            dbc.Col(id='selected_assemblies_preview', style={'textAlign': 'left', 'fontSize': 'calc(5px + 0.5vw)', 'color': 'black'},
                                    width=3),
                            dbc.Col('Plates:', className='input-label', width=2),
                            dbc.Col(id='selected_plates_preview', style={'textAlign': 'left', 'fontSize': 'calc(5px + 0.5vw)', 'color': 'black'},
                                    width=5),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        dbc.Row([
                            dbc.Col('Material:', className='input-label', width=2),
                            dbc.Col(dcc.Dropdown(id='assembly_material_selector', placeholder="", clearable=True,
                                                 persistence=True, persistence_type='session', className='dropdown'), width=3),
                            dbc.Col(id='assembly_material_description', children='Material Description',
                                    className='text-description',
                                    width=7),
                        ], align='center', className='input-row'),

                        dbc.Row([
                            dbc.Col('Plate Type:', className='input-label', width=2),
                            dbc.Col(dcc.Dropdown(id='assembly_plate_selector', placeholder="", clearable=True,
                                                 persistence=True, persistence_type='session', className='dropdown'), width=3),
                            dbc.Col(id='assembly_plate_description', children='Plate Description',
                                    className='text-description',
                                    width=7),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        dbc.Row([
                            html.Button('Apply Changes', id='assembly_apply_button', n_clicks=0,
                                        className='apply-button')
                        ], style={'marginLeft': '11vw', 'marginTop': '1vh'})
                    ], width=8),

                    dbc.Col([
                        # Current Assembly dropdown
                        dbc.Row([
                            dbc.Col("Preview Assembly:", width=6, align="end", className='current-card'),
                            dbc.Col(
                                dcc.Dropdown(id='assembly_selector', placeholder='Select an Assembly', clearable=True,
                                             persistence=True, persistence_type='session',
                                             className='dropdown'),
                                width=6, align="center"),
                        ]),

                        html.Hr(id='assembly_description'),

                        dbc.Row([
                            assembly_tabs
                        ])
                    ], width=4)
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
    result.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
    return result


@callback(
    Output("assembly_material_selector", "options"),
    Input("assembly_material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials]
    # sorting by int value if possible, otherwise place last
    result.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
    return result


@callback(
    Output("assembly_material_description", "children"),
    Input("assembly_material_selector", "value"),
)
def update_material_description(mat_number):
    material = template.all_materials.get(mat_number)
    if material is not None:
        return material.comment
    return "Material Description"


@callback(
    Output("assembly_plate_selector", "options"),
    Input("assembly_plate_selector", "search_value"),
)
def update_plate_options(search_value):
    result = [o for o in template.all_fuel_plates.keys()]
    result.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
    return result


@callback(
    Output("assembly_plate_description", "children"),
    Input("assembly_plate_selector", "value"),
)
def update_material_description(plate_number):
    u_comment = template.all_universe_names.get(plate_number)
    if u_comment is not None:
        return u_comment
    return "Plate Description"


# Assembly plot callback
@callback(
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Output('assembly_plot_camera', 'data'),
    Output('assembly_plot_selected', 'data', allow_duplicate=True),
    Output('assembly_selector', 'value', allow_duplicate=True),
    Input('assembly_plot', 'clickData'),
    State('assembly_plot', 'relayoutData'),
    State('assembly_plot', 'figure'),
    State('assembly_plot_selected', 'data'),
    State('assembly_plot_camera', 'data'),
    State('assembly_selector', 'options'),
    State('select_mode', 'value'),
    prevent_initial_call=True
)
def handle_click_assembly(clickData, relayoutData, figure, selected, camera_data, assembly_options, select_mode):
    if clickData:
        clicked_object = int(clickData['points'][0]['curveNumber'])

        if select_mode == "unselect":
            figure['data'][clicked_object]['color'] = default_color
        elif select_mode == "multi":
            figure['data'][clicked_object]['color'] = selected_color
        else:  # "single"
            if figure['data'] is not None:
                for data in figure['data']:
                    data['color'] = default_color
            figure['data'][clicked_object]['color'] = selected_color

        # if the relayoutData contains camera information, then update the stored camera data
        if relayoutData and 'scene.camera' in relayoutData:
            camera_data = relayoutData['scene.camera']

        # set the camera position to the stored camera position, if one exists
        if camera_data:
            figure['layout']['scene']['camera'] = camera_data

        selected = []
        for i, obj in enumerate(figure['data']):
            if obj['color'] == selected_color:
                selected.append(i)

        return figure, camera_data, selected, assembly_translator[int(clicked_object)]
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Plate plot callback
@callback(
    Output('plate_plot', 'figure', allow_duplicate=True),
    Output('plate_plot_camera', 'data'),
    Output('plate_plot_selected', 'data', allow_duplicate=True),
    Input('plate_plot', 'clickData'),
    State('plate_plot', 'relayoutData'),
    State('plate_plot', 'figure'),
    State('plate_plot_selected', 'data'),
    State('plate_plot_camera', 'data'),
    State('select_mode', 'value'),
    prevent_initial_call=True
)
def handle_click_plate(clickData, relayoutData, figure, selected, camera_data, select_mode):
    if clickData:
        clicked_object = int(clickData['points'][0]['curveNumber'])

        if select_mode == "unselect":
            figure['data'][clicked_object]['color'] = default_color
        elif select_mode == "multi":
            figure['data'][clicked_object]['color'] = selected_color
        else:  # "single"
            for data in figure['data']:
                data['color'] = default_color
            figure['data'][clicked_object]['color'] = selected_color

        if relayoutData and 'scene.camera' in relayoutData:
            camera_data = relayoutData['scene.camera']

        if camera_data:
            figure['layout']['scene']['camera'] = camera_data

        selected = []
        for i, obj in enumerate(figure['data']):
            if obj['color'] == selected_color:
                selected.append(i)

        return figure, camera_data, selected
    return dash.no_update, dash.no_update, dash.no_update


# Section plot callback
@callback(
    Output('section_plot', 'figure', allow_duplicate=True),
    Output('section_plot_camera', 'data'),
    Output('section_plot_selected', 'data', allow_duplicate=True),
    Input('section_plot', 'clickData'),
    State('section_plot', 'relayoutData'),
    State('section_plot', 'figure'),
    State('section_plot_selected', 'data'),
    State('section_plot_camera', 'data'),
    State('select_mode', 'value'),
    prevent_initial_call=True
)
def handle_click_section(clickData, relayoutData, figure, selected, camera_data, select_mode):
    if clickData:
        clicked_object = int(clickData['points'][0]['curveNumber'])

        if select_mode == "unselect":
            figure['data'][clicked_object]['color'] = default_color
        elif select_mode == "multi":
            figure['data'][clicked_object]['color'] = selected_color
        else:  # "single"
            for data in figure['data']:
                data['color'] = default_color
            figure['data'][clicked_object]['color'] = selected_color

        if relayoutData and 'scene.camera' in relayoutData:
            camera_data = relayoutData['scene.camera']

        if camera_data:
            figure['layout']['scene']['camera'] = camera_data

        selected = []
        for i, obj in enumerate(figure['data']):
            if obj['color'] == selected_color:
                selected.append(i)

        return figure, camera_data, selected
    return dash.no_update, dash.no_update, dash.no_update


@callback(
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Output('assembly_plot_selected', 'data', allow_duplicate=True),
    Input('select_all_assemblies', 'n_clicks'),
    State('assembly_plot', 'figure'),
    State('assembly_plot_selected', 'data'),
    prevent_initial_call=True
)
def select_all_assemblies(n, figure, selected):
    if n:
        selected = []
        for i, obj in enumerate(figure['data']):
            obj['color'] = selected_color
            selected.append(i)
        return figure, selected
    return dash.no_update, dash.no_update


@callback(
    Output('plate_plot', 'figure', allow_duplicate=True),
    Output('plate_plot_selected', 'data', allow_duplicate=True),
    Input('select_all_plates', 'n_clicks'),
    State('plate_plot', 'figure'),
    State('plate_plot_selected', 'data'),
    prevent_initial_call=True
)
def select_all_plates(n, figure, selected):
    if n:
        selected = []
        for i, obj in enumerate(figure['data']):
            obj['color'] = selected_color
            selected.append(i)
        return figure, selected
    return dash.no_update, dash.no_update


@callback(
    Output('section_plot', 'figure', allow_duplicate=True),
    Output('section_plot_selected', 'data', allow_duplicate=True),
    Input('select_all_sections', 'n_clicks'),
    State('section_plot', 'figure'),
    State('section_plot_selected', 'data'),
    prevent_initial_call=True
)
def select_all_sections(n, figure, selected):
    if n:
        selected = []
        for i, obj in enumerate(figure['data']):
            obj['color'] = selected_color
            selected.append(i)
        return figure, selected
    return dash.no_update, dash.no_update


@callback(
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Output('plate_plot', 'figure', allow_duplicate=True),
    Output('section_plot', 'figure', allow_duplicate=True),
    Output('assembly_plot_selected', 'data', allow_duplicate=True),
    Output('plate_plot_selected', 'data', allow_duplicate=True),
    Output('section_plot_selected', 'data', allow_duplicate=True),
    Input('unselect_all_button', 'n_clicks'),
    State('assembly_plot', 'figure'),
    State('plate_plot', 'figure'),
    State('section_plot', 'figure'),
    prevent_initial_call=True
)
def reset_all(n, assembly_figure, plate_figure, single_plate_figure):
    if n == 0:
        raise dash.exceptions.PreventUpdate

    for assembly in assembly_figure['data']:
        assembly['color'] = default_color

    for plate in plate_figure['data']:
        plate['color'] = default_color

    for single_plate in single_plate_figure['data']:
        single_plate['color'] = default_color

    return assembly_figure, plate_figure, single_plate_figure, [], [], []


@callback(
    Output('assembly_preview', 'value'),
    Output('plate_preview', 'value'),
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Output('plate_plot', 'figure', allow_duplicate=True),
    Output('section_plot', 'figure', allow_duplicate=True),
    Input('assembly_selector', 'value'),
    Input('assembly_description', 'value'),  # Used to trigger on reload
    State('assembly_plot_selected', 'data'),
    State('plate_plot_selected', 'data'),
    State('section_plot_selected', 'data'),
    State('assembly_plot', 'figure'),
    State('plate_plot', 'figure'),
    State('section_plot', 'figure'),
    prevent_initial_call='initial_duplicate'
)
def update_assembly_preview(assembly_u, descr, assembly_selected, plate_selected, section_selected, assembly_figure, plate_figure, section_figure):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered_id is None:
        # Update plot selections and cameras from dcc.Stores on reload
        for i, obj in enumerate(assembly_figure['data']):
            if i in assembly_selected:
                obj['color'] = selected_color
        for i, obj in enumerate(plate_figure['data']):
            if i in plate_selected:
                obj['color'] = selected_color
        for i, obj in enumerate(section_figure['data']):
            if i in section_selected:
                obj['color'] = selected_color

    if button_id in ['assembly_selector', 'assembly_description'] or ctx.triggered_id is None:
        if assembly_u is not None:
            description_results = ""
            if assembly_u in template.data_comments.keys():
                description_results = template.data_comments.get(assembly_u)

            selected_assembly = template.all_fuel_assemblies.get(assembly_u)
            if selected_assembly is not None:
                assembly_results = f'Fuel Section Cell:\n'
                assembly_results += f'{selected_assembly.fuel_section}'
                assembly_results += f'\n\nFuel Lattice Cell:\n'
                assembly_results += f'{selected_assembly.fuel_lattice}'
                assembly_results += f'\n\nOther Assembly Contents:\n'
                assembly_results += f'\n'.join(str(card) for card in selected_assembly.other_components)

                # Not worth readability sacrifice to use list comprehension
                plate_preview = ""
                for plate_num in OrderedDict.fromkeys(selected_assembly.fuel_lattice.fill):     # OrderedDict to remove duplicates
                    plate_preview += f'Plate Universe {plate_num}:\n'
                    for meat_cell in template.all_fuel_plates.get(plate_num):
                        plate_preview += str(meat_cell) + f'\n'
                    plate_preview += f'\n\n'

                return assembly_results, plate_preview, assembly_figure, plate_figure, section_figure
    return dash.no_update, dash.no_update, assembly_figure, plate_figure, section_figure


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('assembly_selector', 'value', allow_duplicate=True),
    Output('assembly_description', 'value', allow_duplicate=True),
    Input('assembly_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('assembly_plate_selector', 'value'),
    State('assembly_plot_selected', 'data'),
    State('plate_plot_selected', 'data'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, plate, assembly_selected, plate_selected, current_messages):
    if pathname == '/assembly':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'assembly_apply_button' and apply_clicked:
            if plate is None:
                message = f'({timestamp})\tWarning: No plate change selected'
                current_messages.insert(0, html.P(message))
                return current_messages, dash.no_update, ""
            else:
                if not assembly_selected:
                    message = f'({timestamp})\tWarning: No plot assemblies selected'
                    current_messages.insert(0, html.P(message))
                    return current_messages, dash.no_update, ""
                if not plate_selected:
                    message = f'({timestamp})\tWarning: No plot plates selected'
                    current_messages.insert(0, html.P(message))
                    return current_messages, dash.no_update, ""

            for assembly in assembly_selected:
                translated_assembly = assembly_translator[int(assembly)]
                for change_plate in plate_selected:
                    if template.all_fuel_assemblies.get(translated_assembly).fuel_lattice.fill[int(change_plate)+1] is not None:
                        template.all_fuel_assemblies.get(translated_assembly).fuel_lattice.fill[int(change_plate)+1] = plate
                    else:
                        print('Error: Selected assemblies or plates not found')
            message = f'({timestamp})\tApplied changes to Plates {", ".join(str(int(p)+1) for p in plate_selected)} in Assemblies {", ".join(assembly_translator[int(a)] for a in assembly_selected)}'
            current_messages.insert(0, html.P(message))
            return current_messages, dash.no_update, ""

        return current_messages, dash.no_update, ""


@callback(
    Output('selected_assemblies_preview', 'children'),
    Output('selected_plates_preview', 'children'),
    Input('assembly_plot_selected', 'data'),
    Input('plate_plot_selected', 'data'),
    State('assembly_plot', 'figure'),
    State('plate_plot', 'figure'),
    State('assembly_selector', 'options'),
)
def update_selected_on_selected(assembly_selected, plate_selected, assembly_plot, plate_plot, assembly_options):
    # Find highlighted objects in each plot
    assemblies = "None"
    if assembly_selected:
        assemblies = ", ".join(assembly_translator[int(x)] for x in assembly_selected)
    plates = "None"
    if plate_selected:
        plates = ", ".join(str(int(x) + 1) for x in plate_selected)
    return assemblies, plates


assembly_tabs = dcc.Tabs([
    dcc.Tab(label='Assembly',
            className='tab',
            children=dcc.Textarea(
                id='assembly_preview',
                style={
                    'fontSize': 'calc(5px + 0.5vw)',
                    'backgroundColor': '#333333',
                    'color': '#A9A9A9',
                    'border': '3px solid black',
                    'height': '60vh',
                    'width': '100%',
                    'overflow': 'scrollX',
                    'inputMode': 'email',
                },
            )
            ),
    dcc.Tab(label='Plates',
            className='tab',
            children=dcc.Textarea(
                id='plate_preview',
                style={
                    'fontSize': 'calc(5px + 0.5vw)',
                    'backgroundColor': '#333333',
                    'color': '#A9A9A9',
                    'border': '3px solid black',
                    'height': '60vh',
                    'width': '100%',
                    'overflow': 'scrollX',
                    'inputMode': 'email',
                },
            )
            ),
], className='tab-container')
