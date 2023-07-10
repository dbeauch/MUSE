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
                    dbc.Col("Current Surface:", width=3, align="end", className='current-card'),
                    dbc.Col(dcc.Dropdown(id='surface_selector', placeholder='Select a Surface', clearable=True,
                                         persistence=True, persistence_type='session',
                                         className='dropdown'),
                            width=3, align="center")
                ]),
                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        # Description
                        dbc.Row([
                            dbc.Col('Description:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='surface_description', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        # Mnemonic
                        dbc.Row([
                            dbc.Col('Mnemonic:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='mnemonic_input', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        # Transform
                        dbc.Row([
                            dbc.Col('Transform:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='transform_input', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        # Dimensions
                        dbc.Row([
                            dbc.Col('Dimensions:', className='input-label', width=2),
                            dbc.Col(
                                dbc.Input(id='dimensions_input', type='text', className='input-box'))
                        ], align='center', style={'marginTop': 20}),

                        html.Hr(),

                        html.Button('Apply Changes', id='surface_apply_button', n_clicks=0, className='apply-button'),
                    ], width=6),

                    dbc.Col([
                        dcc.Tabs([
                            dcc.Tab(label='Print Preview',
                                    className='tab',
                                    children=dcc.Textarea(
                                        id='surface_preview',
                                        style={
                                            'fontSize': 'calc(5px + 0.5vw)',
                                            'backgroundColor': '#333333',
                                            'color': '#A9A9A9',
                                            'border': '3px solid black',
                                            'height': '60vh',
                                            'width': '40vw',
                                            'overflow': 'scrollX',
                                            'inputMode': 'email',
                                        }, className='scrollbar-hidden'
                                    )
                                    )
                        ], className='tab-container')
                    ], width=6)
                ])
            ], fluid=True),
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
    Output('surface_description', 'value'),
    Output('surface_preview', 'value'),
    Input('surface_selector', 'value'),
)
def update_surface_display(surface):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'surface_selector' or ctx.triggered_id is None:
        if surface is not None:
            selected_surface = template.all_surfaces.get(surface)
            return selected_surface.mnemonic, selected_surface.transform, selected_surface.dimensions, selected_surface.get_comment(), str(
                selected_surface)
        else:
            return "", "", "", "", ""


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('surface_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('surface_selector', 'value'),
    State('surface_description', 'value'),
    State('mnemonic_input', 'value'),
    State('transform_input', 'value'),
    State('dimensions_input', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, surface, description, mnemonic, transform, dimensions, current_messages):
    if pathname == '/surfaces':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'surface_apply_button' and surface is not None:
            if mnemonic is None:
                return current_messages
            selected_surface = template.all_surfaces.get(surface)
            if selected_surface.comment == description and selected_surface.mnemonic == mnemonic and selected_surface.transform == transform and selected_surface.dimensions == dimensions:
                message = f'({timestamp})\tNo changes made to Surface {surface}'
                current_messages.insert(0, html.P(message))
                return current_messages

            if description is not None:
                selected_surface.comment = description

            if mnemonic is not None:
                selected_surface.mnemonic = mnemonic

            if transform is not None:
                selected_surface.transform = transform

            if dimensions is not None:
                selected_surface.dimensions = dimensions

            message = f'({timestamp})\tApplied changes to Surface {surface}'
            current_messages.insert(0, html.P(message))
            return current_messages

        return current_messages
