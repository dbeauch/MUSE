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

                # Current Material dropdown
                dbc.Row([
                    dbc.Col("Current Material:", width=3, align="end", className='current-card'),
                    dbc.Col(dcc.Dropdown(id='material_selector', placeholder='Select a Material', clearable=True,
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
                                dbc.Input(id='material_description', type='text', className='input-box'))
                        ], align='center', className='input-row'),

                        # Zaid
                        dbc.Row([
                            dbc.Col('Zaid:', className='input-label', width=2),
                            dbc.Col(dcc.Dropdown(id='zaid_selector', placeholder='', clearable=True,
                                                 className='dropdown'), width=3),
                        ], align='center', className='input-row'),

                        html.Hr(),

                        dbc.Col(html.Button('Apply Changes', id='material_apply_button', n_clicks=0, className='apply-button'))
                    ], width=6),

                    dbc.Col([
                        dcc.Tabs([
                            dcc.Tab(label='Print Preview',
                                    className='tab',
                                    children=dcc.Textarea(
                                        id='material_preview',
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
    Output("material_selector", "options"),
    Input("material_selector", "search_value"),
)
def update_material_options(search_value):
    result = [o for o in template.all_materials.keys()]
    result.sort()
    return result


@callback(
    Output('material_preview', 'value'),
    Output('material_description', 'value'),
    Output('zaid_selector', 'options'),
    Input('material_selector', 'value'),
    Input('material_description', 'value'),
)
def update_material_display(material, descr):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'material_selector' or ctx.triggered_id is None:
        if material is not None:
            material_results = ""
            description_results = ""
            zaid_list = []
            if material in template.all_materials.keys():
                selected_material = template.all_materials[material]
                material_results = selected_material.__str__(True)
                for zf in selected_material.zaid_fracs:
                    zaid_list.append(zf[0])
            description_results = template.all_materials.get(material).comment
            return material_results, description_results, zaid_list
    return dash.no_update, dash.no_update, dash.no_update


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('material_selector', 'value'),
    Input('material_apply_button', 'n_clicks'),
    State('url', 'pathname'),
    State('material_selector', 'value'),
    State('material_description', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def update_console(apply_clicked, pathname, material, description, current_messages):
    if pathname == '/materials':
        if not current_messages:
            current_messages = []

        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if button_id == 'material_apply_button' and material is not None:
            if description is None:
                return current_messages, dash.no_update
            selected_material = template.all_materials.get(material)
            if selected_material.comment == description:
                message = f'({timestamp})\tNo changes made to Material {material}'
                current_messages.insert(0, html.P(message))
                return current_messages, dash.no_update

            if description is not None:
                selected_material.comment = description

            message = f'({timestamp})\tApplied changes to Material {material}'
            current_messages.insert(0, html.P(message))
            return current_messages, material

        return current_messages, dash.no_update
