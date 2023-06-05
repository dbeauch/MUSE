from dash import Dash, dcc, Input, Output, html
import pandas as pd

app = Dash(__name__)

df = pd.read_csv()

app.layout = html.Div(children=[
                      html.Div(children='''
                        MCNP Editor
                      '''),
                      dcc.Input(id='number', value='', type='int'),
                      dcc.Input(id='material', value='', type='int'),
                      html.Div(id='output'),
])

@app.callback(
    Output(component_id='output', component_property='children'),
    Input(component_id='number', component_property='value'),
    Input(component_id='material', component_property='value'),
)
def update_material(number, material):
    change_material(number, material)
    return f"Surface {number} changed to {material}"


def change_material(number, material):
    return
