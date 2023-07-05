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

                    # Current Material dropdown
                    dbc.Row([
                        dbc.Col(width=1),
                        dbc.Col(html.H4("Current Material:"), width=3, align="end"),
                        dbc.Col(dcc.Dropdown(id='material_selector', placeholder='Select a Material', clearable=True, persistence=True, persistence_type='session'), width=2,
                                align="center"),
                        dbc.Col(html.H5(id='material_description', children='Material Description'), width=6, align="end"),
                    ], justify="center"),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([dbc.Container([


                            html.Hr(),

                            dbc.Row([
                                dbc.Col(html.Button('Apply Changes', id='material_apply_button', n_clicks=0), width=4),
                                dbc.Col(width=7),
                            ], className='g-0', justify='start')
                        ])], width=6),

                        dbc.Col([
                            dcc.Textarea(
                                id='material_display',
                                style={
                                    'backgroundColor': '#333333',
                                    'color': '#A9A9A9',
                                    'border': '3px solid black',
                                    'height': '60vh',
                                    'width': '40vw',
                                    'overflow': 'scrollX',
                                    'inputMode': 'email',
                                },
                            )
                        ], width=6),
                    ]),
                ]),
            ])
        ]


@callback(
    Output("material_selector", "options"),
    Input("material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials.keys()]
    result.sort()
    return result


@callback(
    Output('material_display', 'value'),
    Output('material_description', 'children'),
    Input('material_selector', 'value'),
)
def update_material_display(material):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'material_selector' or ctx.triggered_id is None:
        if material is not None:
            material_results = ""
            description_results = ""
            if material in template.all_materials.keys():
                material_results = template.all_materials[material].__str__(True)
            if material in template.data_comments.keys():
                description_results = template.data_comments.get(material)
            return material_results, description_results
    return "Material Representation", "Material Description"


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('material_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('material_selector', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, material, current_messages):
    if pathname == '/material':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # if button_id == 'material_apply_button' and material is not None:
        #     if something is None:
        #         return current_messages
        #     selected_material = template.all_materials.get(material)
        #     if selected_material == material:
        #         message = f'({timestamp})\tNo changes made to Material {material}'
        #         current_messages.insert(0, html.P(message))
        #         return current_messages
        #
        #     message = f'({timestamp})\tApplied changes to Material {material}'
        #     current_messages.insert(0, html.P(message))
        #     return current_messages

        return current_messages
    else:
        return
