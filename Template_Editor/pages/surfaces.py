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

                    # Current Surface dropdown
                    dbc.Row([
                        dbc.Col(width=1),
                        dbc.Col(html.H4("Current Surface:"), width=3, align="end"),
                        dbc.Col(dcc.Dropdown(id='surface_selector', placeholder='Select a Surface', clearable=True, persistence=True, persistence_type='session'), width=2,
                                align="center"),
                        dbc.Col(html.H5(id='surface_description', children='Surface Description'), width=6, align="end"),
                    ], justify="center"),

                    html.Hr(),

                    # Mnemonic
                    html.H6("Mnemonic:", style={'marginTop': 20}),
                    dbc.Input(id='mnemonic_input', type='text', placeholder=""),

                    # Transform
                    html.H6("Associated Transform:", style={'marginTop': 20}),
                    dbc.Input(id='transform_input', type='text', placeholder=""),

                    # Dimensions
                    html.H6("Dimensions:", style={'marginTop': 20}),
                    dbc.Input(id='dimensions_input', type='text', placeholder=""),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col(html.Button('Apply Changes', id='surface_apply_button', n_clicks=0), width=4),
                        dbc.Col(width=7),
                    ], className='g-0', justify='start')
                ]),
            ])
        ]


@callback(
    Output("surface_selector", "options"),
    Input("surface_selector", "search_value"),
)
def update_surface_options(search_value):
    return [o for o in template.all_surfaces]


@callback(
    Output('mnemonic_input', 'value'),
    Output('transform_input', 'value'),
    Output('dimensions_input', 'value'),
    Output('surface_description', 'children'),
    Input('surface_selector', 'value'),
)
def update_surface_display(surface):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'surface_selector' or ctx.triggered_id is None:
        if surface is not None:
            selected_surface = template.all_surfaces.get(surface)
            return selected_surface.mnemonic, selected_surface.transform, selected_surface.dimensions, selected_surface.comment
        else:
            return "", "", "", "Surface Description"


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('surface_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('surface_selector', 'value'),
    State('mnemonic_input', 'value'),
    State('transform_input', 'value'),
    State('dimensions_input', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, surface, mnemonic, transform, dimensions, current_messages):
    if pathname == '/surfaces':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'surface_apply_button' and surface is not None:
            selected_surface = template.all_surfaces.get(surface)
            if selected_surface.number == surface and selected_surface.mnemonic == mnemonic and selected_surface.transform == transform and selected_surface.dimensions == dimensions:
                message = f'({timestamp})\tNo changes made to Surface {surface}'
                current_messages.insert(0, html.P(message))
                return current_messages

            if mnemonic is not None:
                selected_surface.mnemonic = mnemonic

            if transform is not None:
                selected_surface.transform = transform

            if dimensions is not None:
                selected_surface.geom = dimensions

            message = f'({timestamp})\tApplied changes to Surface {surface}'
            current_messages.insert(0, html.P(message))
            return current_messages

        return current_messages
    else:
        return
