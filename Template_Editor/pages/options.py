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

                    # Current Option dropdown
                    dbc.Row([
                        dbc.Col(width=1),
                        dbc.Col(html.H4("Current Option:"), width=3, align="end"),
                        dbc.Col(dcc.Dropdown(id='option_selector', placeholder='Select an Option', clearable=True, persistence=True, persistence_type='session'), width=2,
                                align="center"),
                        dbc.Col(html.H5(id='option_description', children='Option Description'), width=6, align="end"),
                    ], justify="center"),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([
                            html.H6("Option Contents"),
                            dcc.Textarea(
                                id='option_display',
                                style={
                                    'backgroundColor': '#333333',
                                    'color': '#A9A9A9',
                                    'border': '3px solid black',
                                    'height': '50vh',
                                    'width': '69vw',
                                    'overflow': 'scrollX',
                                    'inputMode': 'email',
                                },
                            )
                        ]),
                    ], className='g-0'),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col(html.Button('Apply Changes', id='option_apply_button', n_clicks=0), width=4),
                        dbc.Col(width=7),
                    ], className='g-0', justify='start')
                ]),
            ])
        ]


@callback(
    Output("option_selector", "options"),
    Input("option_selector", "search_value"),
)
def update_assembly_options(search_value):
    result = [o for o in template.all_options.keys()]
    result.sort()
    return result


@callback(
    Output('option_display', 'value'),
    Output('option_description', 'children'),
    Input('option_selector', 'value'),
)
def update_assembly_display(option):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'option_selector' or ctx.triggered_id is None:
        if option is not None:
            option_results = ""
            description_results = ""
            if option in template.all_options.keys():
                option_results = template.all_options[option].__str__()
            if option in template.data_comments.keys():
                description_results = template.data_comments[option]
            return option_results, description_results
    return "Option Contents", "Option Description"


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('option_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('option_selector', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, option, current_messages):
    if pathname == '/options':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # if button_id == 'option_apply_button' and option is not None:
        #     if something is None:
        #         return current_messages
        #     selected_option = template.all_options.get(option)
        #     if selected_option == option:
        #         message = f'({timestamp})\tNo changes made to Option {option}'
        #         current_messages.insert(0, html.P(message))
        #         return current_messages
        #
        #     message = f'({timestamp})\tApplied changes to Option {option}'
        #     current_messages.insert(0, html.P(message))
        #     return current_messages

        return current_messages
    else:
        return
