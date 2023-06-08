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


def recurse_continue(pieces, start_index, num):
    """
    Helper function for join_card_pieces() that recursively finds how many lines a card contains
    :param pieces: array containing cleaned line pieces
    :param start_index: line index of start of card
    :param num: parameter passed to next
    :return:
    """
    space_index = None
    ampersand_index = re.search(r'[ \t]*&', pieces[start_index + num])
    if len(pieces) - 1 > start_index + num:
        space_index = re.search(r'^ {5,}\S', pieces[start_index + 1 + num])

    if ampersand_index is None and space_index is None:
        return num
    elif ampersand_index is not None:
        pieces[start_index + num] = pieces[start_index + num][0: ampersand_index.span()[0]] + " "
        return recurse_continue(pieces, start_index, num + 1)
    elif space_index is not None:
        pieces[start_index + 1 + num] = pieces[start_index + 1 + num][space_index.span()[1] - 1:] + " "
        return recurse_continue(pieces, start_index, num + 1)
    else:
        print("Error: recurse_continue()")