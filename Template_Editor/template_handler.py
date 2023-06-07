#   Regex for non-void cell cards: ^\d{1,6}[ \t]+\d{1,6}[ \t]+-?\d+(\.\d+)?e?-?\d*[ \t]+\(?-?\d+(([ \t]|:)-?\(?\d+\)?)*\)?[ \t]+.*$
#   Regex for void cell cards: ^\d{1,6}[ \t]+0[ \t]+\(?-?\d+(([ \t]|:)-?\(?\d+\)?)*\)?[ \t]+.*$

import re
cell_line_pieces = []
surface_line_pieces = []
data_line_pieces = []

cell_lines = []
surface_lines = []
data_lines = []

all_cells = {}
all_surfaces = {}
all_materials = {}
all_options = []


def read_template(in_filename):
    f_read = open(in_filename, 'r')
    curr_list = cell_line_pieces
    for line in f_read.readlines():
        if re.search(r'\bBegin Surfaces\b', line):
            curr_list = surface_line_pieces
            break
        elif re.search(r'\bBegin Options\b', line):
            curr_list = data_line_pieces
        curr_list.append(line)
    f_read.close()

    clean_pieces(cell_line_pieces)
    clean_pieces(surface_line_pieces)
    clean_pieces(data_line_pieces)
    print(cell_line_pieces)

    join_card_pieces(cell_line_pieces, cell_lines)
    join_card_pieces(surface_line_pieces, surface_lines)
    join_card_pieces(data_line_pieces, data_lines)
    #make_cards()
    return


def clean_pieces(array):
    i = 0
    for line in array:
        array[i] = line.replace("\n", "")                      # remove \n
        comment_index = re.search(r'[ \t]*\$', line)           # remove $ comment along with leading white space
        if comment_index is not None:
            array[i] = line[0: comment_index.span()[0]]
        if re.search(r'^[ \t]{0,5}[cC]\s', line) is not None:  # remove 'c' comment # TODO: still add to cell_lines
            array.remove(array[i])
            i -= 1
        i += 1
    return

# TODO: Cells following a c are omitted entirely (cell 700)
# TODO: End of cell section is written twice to file

def join_card_pieces(line_pieces, line_array):
    skip = 0
    for i in range(len(line_pieces)):
        if skip > 0:
            skip -= 1
            continue
        result = ""
        num_lines_continues = line_continues(i, line_pieces)
        for j in range(num_lines_continues + 1):
            result += line_pieces[i+j]
        skip += num_lines_continues
        line_array.append(result)
        if i == len(line_pieces):
            break
    return


def line_continues(index, pieces):
    start_line = pieces[index]
    if re.search(r'[ \t]*&', start_line):                        # line continues with & on the next line; & and leading white space removed, one space added after and next line appended
        return recurse_continue(pieces, index, 0)
    elif len(pieces)-1 > index:
        if re.search(r'^ {6,}\S+', pieces[index+1]):
            pieces[index] += " "                                   # Space between continued lines when joined
            return recurse_continue(pieces, index, 0)
    return 0


def recurse_continue(pieces, start_index, num):
    space_index = None
    ampersand_index = re.search(r'[ \t]*&', pieces[start_index + num])
    if len(pieces) - 1 > start_index + num:
        space_index = re.search(r'^ {6,}\S', pieces[start_index + 1 + num])
    if ampersand_index is None and space_index is None:
        return num
    elif ampersand_index is not None:
        pieces[start_index + num] = pieces[start_index + num][0: ampersand_index.span()[0]] + " "
        return recurse_continue(pieces, start_index, num + 1)
    elif space_index is not None:
        pieces[start_index + 1 + num] = pieces[start_index + 1 + num][space_index.span()[1] - 1:] + " "
        return recurse_continue(pieces, start_index, num + 1)   # TODO: this infinite with material cards


def make_cards():

    return


def print_file(out_filename):
    f_write = open(out_filename, 'w')

    for line in cell_lines:
        print(line.strip('\n'), file=f_write)
    """for line in all_surfaces:
        print(line.strip('\n'), file=f_write)
    for line in all_options:
        print(line.strip('\n'), file=f_write)"""
    f_write.close()
    return out_filename
