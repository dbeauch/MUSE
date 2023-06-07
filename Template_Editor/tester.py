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



"""word = "word"
arry = ["c this is a comment", "1 2 3 this is $not", "next", "      line", "      here", "awe4gaw&", "fawer"]
fin = []
print(arry)
template_handler.join_card_pieces(arry, fin)
print(arry)
print(fin)"""
