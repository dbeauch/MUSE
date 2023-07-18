import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np

# Settings for colors
default_color = 'rgb(0, 0, 255)'
selected_color = 'rgb(255, 0, 0)'
bgcolor = 'rgb(200, 200, 200)'

# Settings for the assembly surfaces
assembly_spacing = 2
assembly_radius = 0.5
assembly_height = 6

# Settings for the plate surfaces
group_spacing = 12
plate_spacing = 1
plate_thickness = 8
plate_width = 0.5
plate_height = 8

# Settings for the segmented surfaces
segment_spacing = plate_thickness/30
segment_thickness = segment_spacing
segment_height = plate_height
segment_width = plate_width

# set hoverinfo off of 'none' to debug which object is which


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
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k, hoverinfo='none')


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
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k, hoverinfo='none')


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
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k, hoverinfo='none')


# Creating 30 slices in a plate
def create_plate_slices(center, width, thickness, height, slices=30, color=default_color):
    slice_thickness = thickness / slices
    slice_plots = []
    for i in range(slices):
        slice_center = [center[0], center[1] + i * slice_thickness - thickness / 2, center[2]]
        slice_plots.append(create_3d_segment(slice_center, width, slice_thickness, height, color))
    return slice_plots


# Create 3x3 grid of cylinders
assembly_plots = [
    create_3d_trace([i * assembly_spacing, j * assembly_spacing, 0], assembly_radius, assembly_height, assembly_radius,
                    color='rgb(0, 0, 255)') for i in range(3) for j in range(3)]

# Create two groups of 21 plates stacked vertically and horizontally
plate_plots = [create_3d_plane([j * plate_spacing, 0, i * group_spacing], plate_width, plate_thickness, plate_height,
                               color='rgb(0, 0, 255)') for i in range(2) for j in range(21)]

segment_plots = [create_3d_plane([0, j * segment_spacing, 0], segment_width, segment_thickness, segment_height,
                                 color='rgb(0, 0, 255)') for j in range(30)]

assembly_graph = html.Div([dcc.Graph(
    id='assembly-plot',
    figure={
        'data': assembly_plots,
        'layout': go.Layout(
            title='Fuel Assemblies',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                bgcolor=bgcolor,
                xaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                yaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                zaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                aspectmode='data',
            )
        )
    }, className='d-plot'
),
    html.Div(id='assembly-click-data', style={'display': 'none'})
]
)

plate_graph = html.Div([dcc.Graph(
    id='plate-plot',
    figure={
        'data': plate_plots,
        'layout': go.Layout(
            title='Fuel Plates',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                bgcolor=bgcolor,
                xaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                yaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                zaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                aspectmode='data',
            )
        )
    }, className='d-plot'
),
    html.Div(id='plate-click-data', style={'display': 'none'})
],
)


segment_graph = html.Div([dcc.Graph(
    id='single-plate-plot',
    figure={
        'data': segment_plots,
        'layout': go.Layout(
            title='Single Plate Slices',
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                bgcolor=bgcolor,
                xaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                yaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                zaxis=dict(title=None, autorange=True, showgrid=False, zeroline=False, showticklabels=False, showspikes=False),
                aspectmode='data',
                camera=dict(
                    eye=dict(x=2.5, y=2.5, z=2.5),  # adjust these values to set initial zoom
                )
            )
        )
    }, className='d-plot'
),
    html.Div(id='single-plate-click-data', style={'display': 'none'})
],
)


@callback(
    Output('assembly-plot', 'figure'),
    Output('assembly-click-data', 'children'),
    Input('assembly-plot', 'clickData'),
    State('assembly-plot', 'figure'),
    State('assembly-click-data', 'children'),
    State('assembly-plot', 'relayoutData'),
    prevent_initial_call=True
)
def highlight_cylinder(clickData, figure, clicked_cylinder, camera):
    if clicked_cylinder is not None:
        # Reset color of the previously clicked cylinder to blue
        figure['data'][clicked_cylinder]['color'] = default_color

        # Change color of the currently clicked cylinder to red
    clicked_cylinder = int(clickData['points'][0]['curveNumber'])
    figure['data'][clicked_cylinder]['color'] = selected_color

    if camera is not None and 'scene.camera' in camera:
        figure['layout']['scene']['camera'] = camera['scene.camera']

    return figure, clicked_cylinder


@callback(
    Output('plate-plot', 'figure'),
    Output('plate-click-data', 'children'),
    Input('plate-plot', 'clickData'),
    State('plate-plot', 'figure'),
    State('plate-click-data', 'children'),
    State('plate-plot', 'relayoutData'),
    prevent_initial_call=True
)
def highlight_plate(clickData, figure, clicked_plate, camera):
    if clicked_plate is not None:
        # Reset color of the previously clicked plate to blue
        figure['data'][clicked_plate]['color'] = default_color

        # Change color of the currently clicked plate to red
    clicked_plate = int(clickData['points'][0]['curveNumber'])
    figure['data'][clicked_plate]['color'] = selected_color

    if camera is not None and 'scene.camera' in camera:
        figure['layout']['scene']['camera'] = camera['scene.camera']

    return figure, clicked_plate


@callback(
    Output('single-plate-plot', 'figure'),
    Output('single-plate-click-data', 'children'),
    Input('single-plate-plot', 'clickData'),
    State('single-plate-plot', 'figure'),
    State('single-plate-click-data', 'children'),
    State('single-plate-plot', 'relayoutData'),
    prevent_initial_call=True
)
def highlight_segment(clickData, figure, clicked_segment, camera):
    if clicked_segment is not None:
        # Reset color of the previously clicked segment to blue
        figure['data'][clicked_segment]['color'] = default_color

    # Change color of the currently clicked segment to red
    clicked_segment = int(clickData['points'][0]['curveNumber'])
    figure['data'][clicked_segment]['color'] = selected_color

    if camera is not None and 'scene.camera' in camera:
        figure['layout']['scene']['camera'] = camera['scene.camera']

    return figure, clicked_segment
