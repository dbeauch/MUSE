from dash import Dash, dcc, Input, Output, html, ctx
import template_handler
import re

app = Dash(__name__)

df = template_handler.read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')

app.layout = html.Div(children=[
    html.Div(children='''
                        MCNP Editor
                      '''),
    html.Div(children=[
        dcc.Input(id='number', value='', type='text'),
        dcc.Input(id='material', value='', type='text'),
        dcc.Input(id='filename', value='../mcnp_templates/test.i', type='text'),
    ]),
    html.Button('Submit Edit', id='submit-edit', n_clicks=0),
    html.Button('Print File', id='print-button', n_clicks=0),
    html.Hr(),
    html.Div(id='output'),
    html.Hr(),
    html.Div(id='print_message'),
])


@app.callback(
    Output(component_id='output', component_property='children'),
    Input(component_id='number', component_property='value'),
    Input(component_id='material', component_property='value'),
    Input(component_id='submit-edit', component_property='n_clicks')
)
def change_material(number, material, button):
    message = "Enter cell number and new material"
    if "submit-edit" == ctx.triggered_id and number != "" and material != "":

        message = f"Cell {number} changed to material {material}. (Not actually WIP)"
    return message


@app.callback(
    Output(component_id='print_message', component_property='children'),
    Input(component_id='filename', component_property='value'),
    Input(component_id='print-button', component_property='n_clicks'),
    Input(component_id='number', component_property='value'),
    Input(component_id='material', component_property='value'),
)
def print_button(filename, button, number, material):
    if "print-button" == ctx.triggered_id:
        printed = template_handler.print_file(filename)
        return f"The new file was printed to: {printed}. (Not actually WIP)"
    else:
        return ""


if __name__ == '__main__':
    app.run_server(debug=True)
