import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from Template_Editor.mcnp_cards import *
from Template_Editor.template_handler_instance import template_handler_instance as template


def layout(page_background):
    return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([
                    # Top spacing
                    dbc.Row([dbc.Col(html.H1(" "))]),

                    # Current Assembly dropdown
                    dbc.Row([
                        dbc.Col("Current Assembly:", width=3, align="end", className='current-card'),
                        dbc.Col(dcc.Dropdown(id='assembly_selector', placeholder='Select an Assembly', clearable=True,
                                             persistence=True, persistence_type='session',
                                             style={'width': '10vw', 'textAlign': 'left'}),
                                width=3, align="center"),
                        dbc.Col(html.H5(id='assembly_description', children='Assembly Description'),
                                width=6, align="end"),
                    ]),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([


                            html.Hr(),

                            html.Button('Apply Changes', id='assembly_apply_button', n_clicks=0, className='apply-button')
                        ], width=6),

                        dbc.Col([
                            dcc.Tabs([
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
                                            }, className='scrollbar-hidden'
                                        )
                                        )
                            ], className='tab-container')
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
    result = [o for o in template.all_assembly.keys()]
    result.sort()
    return result


@callback(
    Output('assembly_preview', 'value'),
    Output('assembly_description', 'children'),
    Input('assembly_selector', 'value'),
)
def update_assembly_display(assembly):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'assembly_selector' or ctx.triggered_id is None:
        if assembly is not None:
            if assembly in template.data_comments.keys():
                description_results = template.data_comments.get(assembly)
                return "", description_results
    return "", "Assembly Description"


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('assembly_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('assembly_selector', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, assembly, current_messages):
    if pathname == '/assembly':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # if button_id == 'assembly_apply_button' and assembly is not None:
        #     if something is None:
        #         return current_messages
        #     selected_assembly = template.all_assembly.get(assembly)
        #     if selected_assembly == assembly:
        #         message = f'({timestamp})\tNo changes made to Assembly {assembly}'
        #         current_messages.insert(0, html.P(message))
        #         return current_messages
        #
        #     message = f'({timestamp})\tApplied changes to Assembly {assembly}'
        #     current_messages.insert(0, html.P(message))
        #     return current_messages

        return current_messages
