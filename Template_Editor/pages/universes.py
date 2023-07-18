import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from Template_Editor.controllers.template_handler_instance import template_handler_instance as template


def layout(page_background):
    return [
            html.Div(style={'backgroundColor': page_background, 'height': '100vh'}, children=[
                dbc.Container([
                    # Top spacing
                    dbc.Row([dbc.Col(html.H1(" "))]),

                    # Current Universe dropdown
                    dbc.Row([
                        dbc.Col("Current Universe:", width=6, align="end", className='current-card'),
                        dbc.Col(dcc.Dropdown(id='universe_selector', placeholder='Select a Universe', clearable=True,
                                             persistence=True, persistence_type='session',
                                             className='dropdown'),
                                width=3, align="center")
                    ]),
                    html.Hr(),

                    dbc.Row([
                        # dbc.Col([
                        #     # Description
                        #     dbc.Row([
                        #         dbc.Col('Description:', className='input-label', width=2),
                        #         dbc.Col(
                        #             dbc.Input(id='universe_description', type='text', className='input-box'))
                        #     ], align='center', className='input-row'),
                        #
                        #     html.Hr(),
                        #
                        #     html.Button('Apply Changes', id='universe_apply_button', n_clicks=0, className='apply-button')
                        # ], width=6),

                        dbc.Col([
                            dcc.Tabs([
                                dcc.Tab(label='Universe Contents',
                                        className='tab',
                                        children=dcc.Textarea(
                                            id='universe_contents',
                                            style={
                                                'fontSize': 'calc(5px + 0.5vw)',
                                                'backgroundColor': '#333333',
                                                'color': '#A9A9A9',
                                                'border': '3px solid black',
                                                'height': '60vh',
                                                'width': '80vw',
                                                'overflow': 'scrollX',
                                                'inputMode': 'email',
                                            }, className='scrollbar-hidden'
                                        )
                                        ),
                                dcc.Tab(label='Filled Cells',
                                        className='tab',
                                        children=dcc.Textarea(
                                            id='fill_uses',
                                            style={
                                                'fontSize': 'calc(5px + 0.5vw)',
                                                'backgroundColor': '#333333',
                                                'color': '#A9A9A9',
                                                'border': '3px solid black',
                                                'height': '60vh',
                                                'width': '80vw',
                                                'overflow': 'scrollX',
                                                'inputMode': 'email',
                                            }, className='scrollbar-hidden'
                                        )
                                        )
                            ], className='tab-container')
                        ], width=6),
                    ]),
                ], fluid=True),
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
    Output('universe_contents', 'value'),
    Output('fill_uses', 'value'),
    # Output('universe_description', 'value'),
    Input('universe_selector', 'value'),
    # Input('universe_description', 'value'),
)
def update_universe_display(universe):  # , descr):
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
                description_results = template.all_universe_names.get(universe)
            return universe_results, fill_results  # , description_results
    return dash.no_update, dash.no_update  # , dash.no_update


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('universe_selector', 'value'),
    Input('universe_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('universe_selector', 'value'),
    # State('universe_description', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, universe, current_messages):  # , description
    if pathname == '/universes':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'universe_apply_button' and universe is not None:
            # if description is None or description == "":
            #     return current_messages, dash.no_update
            selected_universe = template.all_universes.get(universe)
            # if selected_universe == universe and template.all_universe_names.get(universe) == description:
            #     message = f'({timestamp})\tNo changes made to Universe {universe}'
            #     current_messages.insert(0, html.P(message))
            #     return current_messages, universe

            # if description is not None or description != "":
            #     template.all_universe_names[universe] = description

            message = f'({timestamp})\tApplied changes to Universe {universe}'
            current_messages.insert(0, html.P(message))
            return current_messages, universe

        return current_messages, dash.no_update
