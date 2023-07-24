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
from Template_Editor.pages.select_graphs import segment_graph
from Template_Editor.pages.select_graphs import selected_color, default_color


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
                                        id="plate_select_mode",
                                        options=[
                                            {"label": "Single Select Mode", "value": "single"},
                                            {"label": "Multiselect Mode", "value": "multi"},
                                            {"label": "Unselect Mode", "value": "unselect"}
                                        ],
                                        value="single"  # Single by default
                                    )),
                                    dbc.Row("Highlight Options", className='input-label', style={'marginTop': '2vh'}),
                                    dbc.Button("All Sections", id='select_all_sections', className='unselect-button'),
                                    dbc.Button("Unselect All", id='plate_unselect_all_button', className='unselect-button')
                                ], className='plot-options'),
                            ], width=4),

                            dcc.Store(id='section_plot_camera', storage_type='session'),

                            dcc.Store(id='section_plot_selected', data=[], storage_type='session'),

                            dbc.Col([  # Plot Tabs
                                dcc.Tabs([
                                    dcc.Tab(label='Segments Plot',
                                            className='tab',
                                            children=segment_graph
                                            ),
                                ], className='tab-container')
                            ], width=8),
                        ]),

                        html.Hr(),

                        dbc.Row([
                            dbc.Col('Sections:', className='input-label', width=2),
                            dbc.Col(id='selected_sections_preview', style={'textAlign': 'left', 'fontSize': 'calc(5px + 0.5vw)', 'color': 'black'},
                                    width=10),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        dbc.Row([
                            dbc.Col('Material:', className='input-label', width=2),
                            dbc.Col(dcc.Dropdown(id='plate_material_selector', placeholder="", clearable=True,
                                                 persistence=True, persistence_type='session', className='dropdown'), width=3),
                            dbc.Col(id='plate_material_description', children='Material Description',
                                    className='text-description',
                                    width=7),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        dbc.Row([
                            html.Button('Apply Changes', id='plate_apply_button', n_clicks=0,
                                        className='apply-button')
                        ], style={'marginLeft': '11vw', 'marginTop': '1vh'})
                    ], width=8),

                    dbc.Col([
                        # Current Plate dropdown
                        dbc.Row([
                            dbc.Col("Preview Plate:", width=6, align="end", className='current-card'),
                            dbc.Col(
                                dcc.Dropdown(id='plate_selector', placeholder='Select an Plate', clearable=True,
                                             persistence=True, persistence_type='session',
                                             className='dropdown'),
                                width=6, align="center"),
                        ]),

                        html.Hr(id='plate_description'),

                        dbc.Row([
                            plate_tabs
                        ])
                    ], width=4)
                ]),
            ], fluid=True),
        ])
    ]


@callback(
    Output("plate_material_selector", "options"),
    Input("plate_material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials]
    # sorting by int value if possible, otherwise place last
    result.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
    return result


@callback(
    Output("plate_material_description", "children"),
    Input("plate_material_selector", "value"),
)
def update_material_description(mat_number):
    material = template.all_materials.get(mat_number)
    if material is not None:
        return material.comment
    return "Material Description"


@callback(
    Output("plate_selector", "options"),
    Input("plate_selector", "search_value"),
)
def update_plate_options(search_value):
    result = [o for o in template.all_fuel_plates.keys()]
    result.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
    return result


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
    State('plate_select_mode', 'value'),
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
    return figure, camera_data, selected


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
    Output('section_plot', 'figure', allow_duplicate=True),
    Output('section_plot_selected', 'data', allow_duplicate=True),
    Input('plate_unselect_all_button', 'n_clicks'),
    State('section_plot', 'figure'),
    prevent_initial_call=True
)
def reset_all(n, single_plate_figure):
    if n == 0:
        raise dash.exceptions.PreventUpdate

    for single_plate in single_plate_figure['data']:
        single_plate['color'] = default_color

    return single_plate_figure, []


@callback(
    Output('plate_preview', 'value'),
    Output('section_plot', 'figure', allow_duplicate=True),
    Input('plate_selector', 'value'),
    Input('plate_description', 'value'),  # Used to trigger on reload
    State('section_plot_selected', 'data'),
    State('section_plot', 'figure'),
    prevent_initial_call='initial_duplicate'
)
def update_plate_preview(plate_u, descr, section_selected, section_figure):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered_id is None:
        # Update plot selections and cameras from dcc.Stores on reload
        for i, obj in enumerate(section_figure['data']):
            if i in section_selected:
                obj['color'] = selected_color

    if button_id in ['plate_selector', 'plate_description'] or ctx.triggered_id is None:
        if plate_u is not None:
            description_results = ""
            if plate_u in template.data_comments.keys():
                description_results = template.data_comments.get(plate_u)

            selected_plate = template.all_fuel_plates.get(plate_u)
            if selected_plate is not None:
                # Not worth readability sacrifice to use list comprehension
                plate_preview = f'Plate Universe {plate_u}:\n'
                for meat_cell in OrderedDict.fromkeys(selected_plate):     # OrderedDict to remove duplicates
                    plate_preview += str(meat_cell) + f'\n'
                plate_preview += f'\n\n'

                return plate_preview, section_figure
    return dash.no_update, section_figure


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('plate_description', 'value', allow_duplicate=True),
    Input('plate_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('plate_selector', 'value'),
    State('section_plot_selected', 'data'),
    State('plate_material_selector', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, plate_u, section_selected, new_mat, current_messages):
    if pathname == '/plate':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'plate_apply_button' and apply_clicked:
            if plate_u is None:
                message = f'({timestamp})\tWarning: No plate change selected'
                current_messages.insert(0, html.P(message))
                return current_messages, ""

            section_cells = list(template.all_fuel_plates.get(plate_u)[int(x)].number for x in section_selected)
            for meat in template.all_fuel_plates.get(plate_u):
                if meat.number in section_cells:
                    meat.material = new_mat
                    if type(meat) is LikeCell:
                        template.dissect_like_param(meat)
            message = f'({timestamp})\tApplied change to Plate {plate_u} for cells {", ".join(section_cells)}'
            current_messages.insert(0, html.P(message))
            return current_messages, ""

        return current_messages, ""


@callback(
    Output('selected_sections_preview', 'children'),
    Input('section_plot_selected', 'data'),
    Input('plate_selector', 'value'),
)
def update_selected_on_selected(section_selected, plate_u):
    sections = "None"
    if section_selected:
        sections = ", ".join(template.all_fuel_plates.get(plate_u)[int(x)].number for x in section_selected)
    return sections


plate_tabs = dcc.Tabs([
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
