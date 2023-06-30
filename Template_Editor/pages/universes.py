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

                    # Current Universe dropdown
                    dbc.Row([
                        dbc.Col(width=1),
                        dbc.Col(html.H4("Current Universe:"), width=3, align="end"),
                        dbc.Col(dcc.Dropdown(id='universe_selector', placeholder='Select a Universe', clearable=True, persistence=True, persistence_type='session'), width=2,
                                align="center"),
                        dbc.Col(html.H5(id='universe_description', children='Universe Description'), width=6, align="end"),
                    ], justify="center"),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([
                            html.H6("Fill Uses"),
                            dcc.Textarea(
                                id='fill_display',
                                style={
                                    'backgroundColor': '#333333',
                                    'color': '#A9A9A9',
                                    'border': '5px solid black',
                                    'height': '50vh',
                                    'width': '30vw',
                                    'overflow': 'scrollX',
                                    'inputMode': 'email',
                                },
                            )
                        ]),
                        dbc.Col([
                            html.H6("Universe Contents"),
                            dcc.Textarea(
                                id='universe_display',
                                style={
                                    'backgroundColor': '#333333',
                                    'color': '#A9A9A9',
                                    'border': '5px solid black',
                                    'height': '50vh',
                                    'width': '30vw',
                                    'overflow': 'scrollX',
                                    'inputMode': 'email',
                                },
                            )
                        ]),
                    ]),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col(html.Button('Apply Changes', id='universe_apply_button', n_clicks=0), width=4),
                        dbc.Col(width=7),
                    ], className='g-0', justify='start')
                ]),
            ])
        ]


@callback(
    Output("universe_selector", "options"),
    Input("universe_selector", "search_value"),
)
def update_universe_options(search_value):
    result = [o for o in template.all_universes.keys()]
    result.sort()
    return result


@callback(
    Output('fill_display', 'value'),
    Output('universe_display', 'value'),
    Output('universe_description', 'children'),
    Input('universe_selector', 'value'),
)
def update_universe_display(universe):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'universe_selector' or ctx.triggered_id is None:
        if universe is not None:
            fill_results = ""
            universe_results = ""
            description_results = ""
            if universe in template.all_fills.keys():
                for card in template.all_fills.get(universe):
                    fill_results += card.__str__() + "\n"
            if universe in template.all_universes.keys():
                for card in template.all_universes.get(universe):
                    universe_results += card.__str__() + "\n"
            if universe in template.all_universe_names.keys():
                for descr in template.all_universe_names.get(universe):
                    description_results += descr + " "
            return fill_results, universe_results, description_results
    return "Related Fill Uses", "Related Universe Cards", "Universe Description"


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('universe_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('universe_selector', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, universe, current_messages):
    if pathname == '/universes':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # if button_id == 'universe_apply_button' and universe is not None:
        #     selected_universe = template.all_universes.get(universe)
        #     if selected_universe == universe:
        #         message = f'({timestamp})\tNo changes made to Surface {universe}'
        #         current_messages.insert(0, html.P(message))
        #         return current_messages
        #
        #     message = f'({timestamp})\tApplied changes to Universe {universe}'
        #     current_messages.insert(0, html.P(message))
        #     return current_messages

        return current_messages
    else:
        return
