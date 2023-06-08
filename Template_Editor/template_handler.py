#   Regex for non-void cell cards: (^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\d+(\.\d+)?e?-?\d*[ \t]+\(?-?\d+(([ \t]|:|#)-?\(?\d+\)?)*\)?[ \t]+.*$)
#   Regex for void cell cards: ^\d{1,6}[ \t]+0[ \t]+\(?-?\d+(([ \t]|:|#)-?\(?\d+\)?)*\)?[ \t]+.*$

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
    """
    Reads from given filename to clean lines and create card objects for the app on launch
    :param in_filename: name of local file to read from
    :return: None
    """
    f_read = open(in_filename, 'r')
    curr_list = cell_line_pieces
    for line in f_read.readlines():
        if re.search(r'\bBegin Surfaces\b', line):
            curr_list = surface_line_pieces
        elif re.search(r'\bBegin Options\b', line):
            curr_list = data_line_pieces
        curr_list.append(line)
    f_read.close()

    clean_pieces(cell_line_pieces)
    clean_pieces(surface_line_pieces)
    clean_pieces(data_line_pieces)

    join_card_pieces(cell_line_pieces, cell_lines)
    join_card_pieces(surface_line_pieces, surface_lines)
    join_card_pieces(data_line_pieces, data_lines)

    # make_cards()
    return


def clean_pieces(array):
    """
    Cleans each entry of array parameter; removes $ comments and C/c comments
    :param array: array to be cleaned
    :return: None
    """
    i = 0
    while i < len(array):
        comment_index = re.search(r'[ \t]*\$', array[i])           # remove $ comment along with leading white space
        if comment_index is not None:
            array[i] = array[i][0: comment_index.span()[0]]
        if re.search(r'^[ \t]{0,5}[cC]\s', array[i]) is not None:  # remove 'c' comments
            array.pop(i)
            i -= 1
        i += 1
    return


def join_card_pieces(line_pieces, line_array):
    """
    Appends lines that have continuations with '&' at end of line or leading white space
    :param line_pieces: array containing un-joined lines
    :param line_array: array to contain consolidated lines
    :return: None
    """
    index = 0
    while index < len(line_pieces):
        result = ""
        num_lines_continues = 0

        start_line = line_pieces[index]                   # line continues with & on the next line; & and leading white
        if re.search(r'[ \t]*&', start_line):             # space removed, one space added after and next line appended
            num_lines_continues = recurse_continue(line_pieces, index)
        elif len(line_pieces) - 1 > index:
            if re.search(r'^ {5,}\S+', line_pieces[index + 1]):
                num_lines_continues = recurse_continue(line_pieces, index)

        for j in range(num_lines_continues + 1):
            result += line_pieces[index + j] + " "
        index += num_lines_continues
        result = result.replace("\n", "")                  # remove \n
        result = re.sub(r'[ \t]{2,}', " ", result)
        line_array.append(result)
        index += 1
    return


def recurse_continue(pieces, start_index, num=0):
    """
    Helper function for join_card_pieces() that recursively finds how many lines a card contains
    :param pieces: array containing cleaned line pieces
    :param start_index: line index of start of card
    :param num: parameter passed to next call; initial call should be 0
    :return: final num param
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


def make_cards():
    return


def print_file(out_filename):
    f_write = open(out_filename, 'w')

    for line in cell_lines:
        print(line.strip('\n'), file=f_write)
    print("c Begin Surface Cards:", file=f_write)
    for line in surface_lines:
        print(line.strip('\n'), file=f_write)
    print("c Begin Data Cards:", file=f_write)
    for line in data_lines:
        print(line.strip('\n'), file=f_write)

    f_write.close()
    return out_filename
