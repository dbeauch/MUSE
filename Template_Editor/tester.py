import re, template_handler

# original update function from "Submit Edit" button
"""@app.callback(
    Output(component_id='output', component_property='children'),
    Input(component_id='number', component_property='value'),
    Input(component_id='material', component_property='value'),
    Input(component_id='submit-edit', component_property='n_clicks')
)
def change_material(number, material, button):
    message = "Enter cell number and new material"
    if "submit-edit" == ctx.triggered_id and number != "" and material != "":
        regex_search = r'^' + re.escape(number) + r'\s+\d+\s'
        for i in range(len(template_handler.all_cells)):
            line = template_handler.all_cells[i]
            if re.search(regex_search, line) is not None:
                template_handler.all_cells[i] = re.sub(regex_search, f"{number}\t{material}", line)
                message = f"Cell {number} changed to {material}"
            elif re.search(regex_search, line) is None:
                message = "Did not find cell"
    return message
"""

line1 = "1 0 8:9:-10 tmp=2.747-8 imp:n,p=0"
line2 = "2 4 -0.99180 -7 -9 10 (11:21:-31) (-1001:1006:-2001:2006:-31:898) (-4030:4031:4032:-4033:4034) ( 4130:4131:4132:-4133:4134) (-5030:5031:5032:-4033:4034) ( 5330:5331:5332:-4133:4134) (-9110:9111:-9104:9107:9109) (9100:9109) (9103:9109) (-9210:9211:-9204:9207:9209) (9200:9209) (9203:9209) (-9310:9311:-9304:9307:9309) (9300:9309) (9303:9309) (-9410:9411:-9404:9407:9409) (9400:9409) (9403:9409) tmp=2.747-8 imp:n,p=1"
line3 = "56 like 55 but *trcl=( 0.00 5.175 0) "
line = line3

#card = template_handler.make_cell(line2)
#card = template_handler.make_void_cell(line1)
card = template_handler.make_like_but_cell(line3)

print(line)
print(card.number)
print(card.related_cell)
print(card.changes)
# print(card.material)
# print(card.density)
# print(card.geom)
# print(card.params)
print(card)
