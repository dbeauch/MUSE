import re
from mcnp_cards import *

all_cell_lines = []

all_cells = {}
all_surfaces = {}
all_materials = {}


def correct_comments(array):
    i = 0
    while i < len(array):
        dollar_index = re.search(r'\$ .*$', array[i])
        if dollar_index is not None:
            new_comment = "C " + array[i][dollar_index.span()[0] + 1:]
            array[i] = array[i][: dollar_index.span()[0]]
            array.insert(i, new_comment)
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
        if re.search(r'^[cC] .*$', line_pieces[index]) is None:
            result = ""
            num_lines_continues = 0

            start_line = line_pieces[index]
            if re.search(r'[ \t]*&', start_line):
                num_lines_continues = _recurse_continue(line_pieces, index)
            elif len(line_pieces) - 1 > index:
                if re.search(r'^ {5,}\S+', line_pieces[index + 1]):
                    num_lines_continues = _recurse_continue(line_pieces, index)

            for j in range(num_lines_continues + 1):
                result += line_pieces[index + j] + " "
            index += num_lines_continues
            result = result.replace("\n", "")  # remove \n
            result = re.sub(r'[ \t]{2,}', " ", result)  # remove extra spaces
            line_array.append(result)
        index += 1
    return


def _recurse_continue(pieces, start_index, num=0):
    """
        Helper function for join_card_pieces() that recursively finds how many lines a card contains
        :param pieces: array containing cleaned line pieces
        :param start_index: line index of start of card
        :param num: parameter passed to next call; initial call should be 0
        :return: final num param
        """
    if re.search(r'^[cC] .*$', pieces[start_index]) is None:
        space_index = None
        ampersand_index = re.search(r'[ \t]*&', pieces[start_index + num])
        if len(pieces) - 1 > start_index + num:
            space_index = re.search(r'^ {5,}\S', pieces[start_index + 1 + num])

        if ampersand_index is None and space_index is None:
            return num
        elif ampersand_index is not None:
            pieces[start_index + num] = pieces[start_index + num][0: ampersand_index.span()[0]] + " "
            return _recurse_continue(pieces, start_index, num + 1)
        elif space_index is not None:
            pieces[start_index + 1 + num] = pieces[start_index + 1 + num][space_index.span()[1] - 1:] + " "
            return _recurse_continue(pieces, start_index, num + 1)
        else:
            print("Error: recurse_continue()")
    else:
        pieces.pop(start_index+num)
        _recurse_continue(pieces, start_index, num)


def make_cards(line_array):
    """
    Creates card objects from array of lines given by calling CardFactory
    :param line_array: Array of lines
    :return: None
    """
    factory = CardFactory()
    i = 0
    while i < len(line_array):
        if re.search(r'^[cC] .*$', line_array[i]) is not None:
            if re.search(r'^[cC] .*$', line_array[i + 1]) is None:
                comment = line_array[i]
                made_card = factory.create_card(line_array[i], comment)
                i += 1
            else:
                continue
        else:
            made_card = factory.create_card(line_array[i])
        if isinstance(made_card, Cell):
            all_cells[made_card.number] = made_card
        elif isinstance(made_card, Surface):
            all_surfaces[made_card.number] = made_card
        elif isinstance(made_card, Material):
            all_materials[made_card.number] = made_card
        # elif isinstance(made_card, Temperature):
        #     self.all_temperatures[made_card.number] = made_card
        # elif isinstance(made_card, Option):
        #     self.all_options[made_card.code] = made_card
        else:
            print(f"Card for {made_card} with line {line_array[i]} not found")
        i += 1
    return


lits = [
    'c --Begin Cells--                          ',
    '1      0          8:9:-10  tmp=2.747-8 imp:n,p=0                               $ outside of water pool',
    '2      4 -0.99180 -7 -9 10 (11:21:-31)                                         $ light water pool   ',
    '                  (-1001:1006:-2001:2006:-31:898)  ',
    'c cold sources:',
    '                  (-4030:4031:4032:-4033:4034)',
    '                  ( 4130:4131:4132:-4133:4134)',
    '                  (-5030:5031:5032:-4033:4034)',
    '                  ( 5330:5331:5332:-4133:4134)',
    'c beam tubes:',
    '             (-9110:9111:-9104:9107:9109) (9100:9109) (9103:9109)',
    '             (-9210:9211:-9204:9207:9209) (9200:9209) (9203:9209)',
    '             (-9310:9311:-9304:9307:9309) (9300:9309) (9303:9309)',
    '             (-9410:9411:-9404:9407:9409) (9400:9409) (9403:9409)',
    '                  tmp=2.747-8 imp:n,p=1                             ',
    '3      5 -6.55    -11 -21 31 (1:2:-3)                                          $ heavy water outer tank container                  ',
    '                  (1006:-1001:2006:-2001)',
]
correct_comments(lits)
print(lits)
join_card_pieces(lits, all_cell_lines)
print(all_cell_lines)
make_cards(all_cell_lines)
print(all_cells)
