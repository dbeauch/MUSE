import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np

app = dash.Dash(__name__)

# Settings
assembly_spacing = 1.5
assembly_radius = 0.5
assembly_height = 1

group_spacing = 5
plate_spacing = 5
plate_thickness = 0.5
plate_width = 2
plate_height = 2


def create_3d_trace(center, width, height, thickness, color='rgb(0, 0, 255)'):
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
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k)


def create_3d_plane(center, width, thickness, height, color='rgb(0, 0, 255)'):
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
    return go.Mesh3d(x=x, y=y, z=z, color=color, opacity=1, i=i, j=j, k=k)


# Create 3x3 grid of cylinders
assembly_plots = [
    create_3d_trace([i * assembly_spacing, j * assembly_spacing, 0], assembly_radius, assembly_height, assembly_radius,
                    color='rgb(0, 0, 255)') for i in range(3) for j in range(3)]

# Create two groups of 21 plates stacked vertically and horizontally
plate_plots = [create_3d_plane([j * plate_spacing, 0, i * group_spacing], plate_width, plate_thickness, plate_height,
                               color='rgb(0, 0, 255)') for i in range(2) for j in range(21)]

app.layout = html.Div([
    dcc.Graph(
        id='assembly-plot',
        figure={
            'data': assembly_plots,
            'layout': go.Layout(
                title='Fuel Assemblies',
                scene=dict(
                    xaxis=dict(autorange=True, showgrid=True, zeroline=False, showticklabels=False),
                    yaxis=dict(autorange=True, showgrid=True, zeroline=False, showticklabels=False),
                    zaxis=dict(autorange=True, showgrid=True, zeroline=False, showticklabels=False),
                    aspectmode='cube'
                )
            )
        }
    ),
    html.Div(id='assembly-click-data', style={'display': 'none'}),

    dcc.Graph(
        id='plate-plot',
        figure={
            'data': plate_plots,
            'layout': go.Layout(
                title='Fuel Plates',
                scene=dict(
                    xaxis=dict(autorange=True, showgrid=True, zeroline=False, showticklabels=False),
                    yaxis=dict(autorange=True, showgrid=True, zeroline=False, showticklabels=False),
                    zaxis=dict(autorange=True, showgrid=True, zeroline=False, showticklabels=False),
                    aspectmode='cube'
                )
            )
        }
    ),
    html.Div(id='plate-click-data', style={'display': 'none'})
])


@app.callback(
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
        figure['data'][clicked_cylinder]['color'] = 'rgb(0, 0, 255)'

        # Change color of the currently clicked cylinder to red
    clicked_cylinder = int(clickData['points'][0]['curveNumber'])
    figure['data'][clicked_cylinder]['color'] = 'rgb(255, 0, 0)'

    if camera is not None and 'scene.camera' in camera:
        figure['layout']['scene']['camera'] = camera['scene.camera']

    return figure, clicked_cylinder


@app.callback(
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
        figure['data'][clicked_plate]['color'] = 'rgb(0, 0, 255)'

        # Change color of the currently clicked plate to red
    clicked_plate = int(clickData['points'][0]['curveNumber'])
    figure['data'][clicked_plate]['color'] = 'rgb(255, 0, 0)'

    if camera is not None and 'scene.camera' in camera:
        figure['layout']['scene']['camera'] = camera['scene.camera']

    return figure, clicked_plate


if __name__ == '__main__':
    app.run_server(debug=True)
