from dash import Dash, dcc, Input, Output, html, State, ctx
import template
import re

app = Dash(__name__)

df = template.read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')

app.layout = html.Div(children=[
    html.Div(children='''
                        MCNP Editor
                      '''),
    html.Div(children=[
        dcc.Input(id='number', value='', type='text'),
        dcc.Input(id='material', value='', type='text'),
        dcc.Input(id='filename', value='File to print to', type='text'),
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
        regex_search = r'^' + re.escape(number) + r'\s+\d+\s'
        for i in range(len(template.all_cells)):
            line = template.all_cells[i]
            if re.search(regex_search, line) is not None:
                template.all_cells[i] = re.sub(regex_search, f"{number}\t{material}", line)
                message = f"Cell {number} changed to {material}"
            elif re.search(regex_search, line) is None:
                message = "Did not find cell"
    return message


@app.callback(
    Output(component_id='print_message', component_property='children'),
    Input(component_id='filename', component_property='value'),
    Input(component_id='print-button', component_property='n_clicks'),
)
def print_button(filename, button):
    if "print-button" == ctx.triggered_id:
        printed = template.print_file(filename)
        return f"The new file was printed to: {printed}"
    else:
        return ""


if __name__ == '__main__':
    app.run_server(debug=True)
