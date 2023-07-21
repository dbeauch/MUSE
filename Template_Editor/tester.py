from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
import dash

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
segment_thickness = 4
segment_height = 1
segment_width = 1
segment_spacing = segment_height + 0.5
column_spacing = segment_thickness + 0.5

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


segment_plots = [create_3d_plane([0, j * column_spacing, i * segment_spacing], segment_width, segment_thickness, segment_height,
                                 color=default_color) for i in range(10) for j in range(3)]

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

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True
)
app.layout = html.Div(
    dbc.Col([  # Plot Tabs
        dcc.Tabs([
            dcc.Tab(label='Segments Plot',
                    className='tab',
                    children=segment_graph
                    ),
        ], className='tab-container')
    ], width=8),
)
if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
