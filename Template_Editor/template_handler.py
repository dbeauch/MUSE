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
        elif re.search(r'\bBegin Options\b', line):
            curr_list = data_line_pieces

        curr_list.append(line)
    f_read.close()

    clear_dollar_comments(cell_line_pieces)
    clear_dollar_comments(surface_line_pieces)
    clear_dollar_comments(data_line_pieces)
    join_card_pieces(cell_line_pieces, cell_lines)
    join_card_pieces(surface_line_pieces, surface_lines)
    join_card_pieces(data_line_pieces, data_lines)
    make_cards()
    return


def clear_dollar_comments(array):
    i = 0
    for line in array:
        comment_index = re.search(r'\$', line)  # line has a '$' comment; removed along with leading white space
        if comment_index:
            array[i] = line[0: comment_index.span()[0]]
        i += 1
    return


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
    return


def line_continues(index, pieces):
    start_line = pieces[index]
    if re.search(r'^[ \t]{0,5}[cC]\s', start_line) is not None:    # line is a 'c' comment so still added to cell_lines
        return 0
    if re.search(r'[ \t]*&', start_line):                                           # line continues with & on the next line; & and leading white space removed, one space added after and next line appended
        return recurse_ampersand(pieces, index, 0)
    if re.search(r'^ {6,}\S+', pieces[index+1]):
        return recurse_space(pieces, index, 0)
    return 0


def recurse_ampersand(pieces, start_index, num):
    ampersand_index = re.search(r'[ \t]*&', pieces[start_index + num])
    if ampersand_index is None:
        return num
    else:
        pieces[start_index + num] = pieces[start_index + num][0: ampersand_index.span()[0]] + " "
        return recurse_ampersand(pieces, start_index, num + 1)


def make_cards():

    return


def print_file(out_filename):
    f_write = open(out_filename, 'w')

    """for line in all_cells:
        print(line.strip('\n'), file=f_write)
    for line in all_surfaces:
        print(line.strip('\n'), file=f_write)
    for line in all_options:
        print(line.strip('\n'), file=f_write)"""
    f_write.close()
    return out_filename
