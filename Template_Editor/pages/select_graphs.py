from dash import html, dcc
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
plate_thickness = 12
plate_width = 1
plate_height = 12
group_spacing = plate_thickness + 1
plate_spacing = plate_width + 1.5

# Settings for the segmented surfaces
segment_thickness = 3.3
segment_height = 1
segment_width = 1
segment_spacing = segment_height + 0.5
column_spacing = segment_thickness + 0.5

# Fuel Management Scheme
assembly_translator = [
    '23', '11', '31',
    '32', '12', '22',
    '21', '13', '33',
]


def create_3d_trace(center, width, height, thickness, color=default_color):
    # x, y, z define vertices of rectangular prism
    x = np.array([width / 2, width / 2, -width / 2, -width / 2, width / 2, width / 2, -width / 2, -width / 2]) + center[
        0]
    y = np.array(
        [thickness / 2, -thickness / 2, -thickness / 2, thickness / 2, thickness / 2, -thickness / 2, -thickness / 2,
         thickness / 2]) + center[1]
    z = np.array([height / 2, height / 2, height / 2, height / 2, -height / 2, -height / 2, -height / 2, -height / 2]) + \
        center[2]
    # Vertices of triangles for each face
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

# One (Two) group(s) of 21 plates stacked vertically and horizontally
groups = 1  # (2)
plate_plots = [create_3d_plane([-j * plate_spacing, 0, i * group_spacing], plate_width, plate_thickness, plate_height,
                               color=default_color) for i in range(groups) for j in range(21)]

segment_plots = [create_3d_plane([0, j * column_spacing, i * segment_spacing], segment_width, segment_thickness, segment_height,
                                 color=default_color) for i in range(10) for j in range(3)]

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
    }, config={'displayModeBar': False}, className='d-plot'
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
    }, config={'displayModeBar': False}, className='d-plot'
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
    }, config={'displayModeBar': False}, className='d-plot'
),
    html.Div(id='single-plate-click-data', style={'display': 'none'})
],
)
