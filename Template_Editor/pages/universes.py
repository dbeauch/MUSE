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
                        dbc.Col(dcc.Dropdown(id='universe_selector', placeholder='Select a Universe', clearable=True), width=2,
                                align="center"),
                        dbc.Col(html.H5(id='universe_description', children='Universe Description'), width=6, align="end"),
                    ], justify="center"),

                    html.Hr(),

                    dcc.Textarea(
                        id='universe_display',
                        style={
                            'backgroundColor': '#333333',
                            'color': '#A9A9A9',
                            'border': '5px solid black',
                            'height': '60vh',
                            'width': '69vw',
                            'overflow': 'scroll',
                            'inputMode': 'email',
                        },
                    ),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col(html.Button('Apply Changes', id='universe_apply_button', n_clicks=0), width=4),
                        dbc.Col(width=7),
                        dbc.Col(html.Button('Print File', id='universe_print_button', n_clicks=0), width=1),
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
    Output('universe_display', 'value'),
    Input('universe_selector', 'value'),
    prevent_initial_call=True
)
def update_universe_display(universe):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'universe_selector':
        if universe is not None:
            results = ""
            if universe in template.all_universes.keys():
                for card in template.all_universes.get(universe):
                    message = card.__str__() + "\n"
                    # message = card.number + card.get_inline_comment()
                    results += message
            return results
        else:
            return "Related Universe Cards"


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('universe_apply_button', 'n_clicks'),
    Input('universe_print_button', 'n_clicks'),
    State('url', 'pathname'),
    State('universe_selector', 'value'),
    State('file_path', 'value'),
    State('element_comments', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, print_clicked, pathname, universe, file_path, element_comments, current_messages):
    if pathname == '/universes':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'surface_apply_button' and universe is not None:
            selected_universe = template.all_universes.get(universe)
            if selected_universe.number == universe:
                message = f'({timestamp})\tNo changes made to Surface {universe}'
                current_messages.insert(0, html.P(message))
                return current_messages

            # if data is not None:
            #     selected_universe.data = data

            message = f'({timestamp})\tApplied changes to Universe {universe}'
            current_messages.insert(0, html.P(message))
            return current_messages

        elif button_id == 'universe_print_button':
            element_comments = element_comments == []
            printed = template.print_file(file_path, element_comments)
            message = f'({timestamp})\tPrinted the file to: {printed}'
            current_messages.insert(0, html.P(message))

        return current_messages
    else:
        return
