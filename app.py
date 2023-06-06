from dash import Dash, dcc, Input, Output, html, State, ctx
#import pandas as pd

app = Dash(__name__)

df = read_template('mcnp_templates/burn_Box9_v02_SU_cycle8.i')

app.layout = html.Div(children=[
    html.Div(children='''
                        MCNP Editor
                      '''),
    html.Div(children=[
        dcc.Input(id='number', value='', type='text'),
        dcc.Input(id='material', value='', type='text'),
    ]),
    html.Button('Submit Edit', id='submit-edit', n_clicks=0),
    html.Hr(),
    html.Div(id='output'),
])


@app.callback(
    Output(component_id='output', component_property='children'),
    Input(component_id='number', component_property='value'),
    Input(component_id='material', component_property='value'),
    Input(component_id='submit-edit', component_property='n_clicks')
)
def change_material(number, material, button):
    message = "Enter cell number and new material"
    if "submit-edit" == ctx.triggered_id:
        f_read = open('mcnp_templates/burn_Box9_v02_SU_cycle8.i', 'r')
        f_write = open('mcnp_templates/test.i', 'w')
        new_file = []

        for line in f_read.readlines():
            new_file.append(line)

        for i in range(len(new_file)):
            line = new_file[i]
            #if line.contains(f"m{number} "):

            print(line.strip('\n'), file=f_write)

        f_read.close()
        f_write.close()
        if number != "" and material != "":
            message = f"Cell {number} changed to {material}"
    return message


if __name__ == '__main__':
    app.run_server(debug=True)
