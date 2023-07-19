import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np

# Settings for plot colors/light
default_color = 'rgb(70,130,225)'
selected_color = 'rgb(255,127,80)'
bgcolor = 'rgb(211,211,211)'
lighting_effects = dict(ambient=0.7, diffuse=0.8, fresnel=0.2, specular=0.2, roughness=1)

# Settings for the assembly surfaces
assembly_spacing = 2
assembly_radius = 0.5
assembly_height = 6

# Settings for the plate surfaces
group_spacing = 12
plate_spacing = 1.5
plate_thickness = 8
plate_width = 0.5
plate_height = 8

# Settings for the segmented surfaces
segment_spacing = plate_thickness / 30
segment_thickness = segment_spacing
segment_height = plate_height
segment_width = plate_width


def create_3d_trace(center, width, height, thickness, color=default_color):
    x = np.array([width / 2, width / 2, -width / 2, -width / 2, width / 2, width / 2, -width / 2, -width / 2]) + center[
        0]
    y = np.array(
        [thickness / 2, -thickness / 2, -thickness / 2, thickness / 2, thickness / 2, -thickness / 2, -thickness / 2,
         thickness / 2]) + center[1]
    z = np.array([height / 2, height / 2, height / 2, height / 2, -height / 2, -height / 2, -height / 2, -height / 2]) + \
        center[2]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k,
                     lighting=lighting_effects)  # , hoverinfo='none')


def create_3d_plane(center, width, thickness, height, color=default_color):
    x = np.array([width / 2, width / 2, -width / 2, -width / 2, width / 2, width / 2, -width / 2, -width / 2]) + center[
        0]
    y = np.array(
        [thickness / 2, -thickness / 2, -thickness / 2, thickness / 2, thickness / 2, -thickness / 2, -thickness / 2,
         thickness / 2]) + center[1]
    z = np.array([height / 2, height / 2, height / 2, height / 2, -height / 2, -height / 2, -height / 2, -height / 2]) + \
        center[2]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k,
                     lighting=lighting_effects)  # , hoverinfo='none')


def create_3d_segment(center, width, thickness, height, color=default_color):
    x = np.array([width / 2, width / 2, -width / 2, -width / 2, width / 2, width / 2, -width / 2, -width / 2]) + center[
        0]
    y = np.array(
        [thickness / 2, -thickness / 2, -thickness / 2, thickness / 2, thickness / 2, -thickness / 2, -thickness / 2,
         thickness / 2]) + center[1]
    z = np.array([height / 2, height / 2, height / 2, height / 2, -height / 2, -height / 2, -height / 2, -height / 2]) + \
        center[2]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k,
                     lighting=lighting_effects)  # , hoverinfo='none')


# 30 slices in a plate
def create_plate_slices(center, width, thickness, height, slices=30, color=default_color):
    slice_thickness = thickness / slices
    slice_plots = []
    for i in range(slices):
        slice_center = [center[0], center[1] + i * slice_thickness - thickness / 2, center[2]]
        slice_plots.append(create_3d_segment(slice_center, width, slice_thickness, height, color))
    return slice_plots


# 3x3 grid of cylinders
assembly_plots = [
    create_3d_trace([i * assembly_spacing, j * assembly_spacing, 0], assembly_radius, assembly_height, assembly_radius,
                    color=default_color) for i in range(3) for j in range(3)]

# Two groups of 21 plates stacked vertically and horizontally
plate_plots = [create_3d_plane([j * plate_spacing, 0, i * group_spacing], plate_width, plate_thickness, plate_height,
                               color=default_color) for i in range(2) for j in range(21)]

segment_plots = [create_3d_plane([0, j * segment_spacing, 0], segment_width, segment_thickness, segment_height,
                                 color=default_color) for j in range(30)]

assembly_graph = html.Div([dcc.Graph(
    id='assembly_plot',
    figure={
        'data': assembly_plots,
        'layout': go.Layout(
            title='Fuel Assemblies',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                bgcolor=bgcolor,
                xaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                yaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                zaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                aspectmode='data',
            )
        )
    }, className='d-plot'
),
    html.Div(id='assembly-click-data', style={'display': 'none'})
]
)

plate_graph = html.Div([dcc.Graph(
    id='plate_plot',
    figure={
        'data': plate_plots,
        'layout': go.Layout(
            title='Fuel Plates',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                bgcolor=bgcolor,
                xaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                yaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                zaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                aspectmode='data',
            )
        )
    }, className='d-plot'
),
    html.Div(id='plate-click-data', style={'display': 'none'})
],
)

segment_graph = html.Div([dcc.Graph(
    id='section_plot',
    figure={
        'data': segment_plots,
        'layout': go.Layout(
            title='Single Plate Slices',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                bgcolor=bgcolor,
                xaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                yaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                zaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False,
                           showspikes=False),
                aspectmode='data',
                camera=dict(
                    eye=dict(x=2.5, y=2.5, z=2.5),  # Set initial zoom
                )
            )
        )
    }, className='d-plot'
),
    html.Div(id='single-plate-click-data', style={'display': 'none'})
],
)


# Assembly plot callback
@callback(
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Output('assembly_plot_camera', 'data'),
    Input('assembly_plot', 'clickData'),
    Input('assembly_plot', 'relayoutData'),
    State('assembly_plot', 'figure'),
    State('assembly_plot_camera', 'data'),
    State('select_mode', 'value'),
    prevent_initial_call=True
)
def handle_click_assembly(clickData, relayoutData, figure, camera_data, select_mode):
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

    # if the relayoutData contains camera information, then update the stored camera data
    if relayoutData and 'scene.camera' in relayoutData:
        camera_data = relayoutData['scene.camera']

    # set the camera position to the stored camera position, if one exists
    if camera_data:
        figure['layout']['scene']['camera'] = camera_data

    return figure, camera_data


# Plate plot callback
@callback(
    Output('plate_plot', 'figure', allow_duplicate=True),
    Output('plate_plot_camera', 'data'),
    Input('plate_plot', 'clickData'),
    Input('plate_plot', 'relayoutData'),
    State('plate_plot', 'figure'),
    State('plate_plot_camera', 'data'),
    State('select_mode', 'value'),
    prevent_initial_call=True
)
def handle_click_plate(clickData, relayoutData, figure, camera_data, select_mode):
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

    return figure, camera_data


# Section plot callback
@callback(
    Output('section_plot', 'figure', allow_duplicate=True),
    Output('section_plot_camera', 'data'),
    Input('section_plot', 'clickData'),
    Input('section_plot', 'relayoutData'),
    State('section_plot', 'figure'),
    State('section_plot_camera', 'data'),
    State('select_mode', 'value'),
    prevent_initial_call=True
)
def handle_click_section(clickData, relayoutData, figure, camera_data, select_mode):
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

    return figure, camera_data


@callback(
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Output('plate_plot', 'figure', allow_duplicate=True),
    Output('section_plot', 'figure', allow_duplicate=True),
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

    return assembly_figure, plate_figure, single_plate_figure


@callback(
    Output('assembly_plot', 'figure', allow_duplicate=True),
    Input('select_all_assemblies', 'value'),
    State('assembly_plot', 'figure'),
    prevent_initial_call=True
)
def select_all_assemblies(switch, assembly_figure):
    if switch:
        for assembly in assembly_figure['data']:
            assembly['color'] = selected_color
        return assembly_figure
    return dash.no_update


@callback(
    Output('plate_plot', 'figure', allow_duplicate=True),
    Input('select_all_plates', 'value'),
    State('plate_plot', 'figure'),
    prevent_initial_call=True
)
def select_all_plates(switch, plate_figure):
    if switch:
        for plate in plate_figure['data']:
            plate['color'] = selected_color
        return plate_figure
    return dash.no_update


@callback(
    Output('section_plot', 'figure', allow_duplicate=True),
    Input('select_all_sections', 'value'),
    State('section_plot', 'figure'),
    prevent_initial_call=True
)
def select_all_sections(switch, section_figure):
    if switch:
        for section in section_figure['data']:
            section['color'] = selected_color
        return section_figure
    return dash.no_update
