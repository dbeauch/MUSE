from mcnp_cards import *


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class TemplateHandler(Singleton):
    file_title = ""
    cell_line_pieces = []
    surface_line_pieces = []
    data_line_pieces = []

    cell_lines = []
    surface_lines = []
    data_lines = []

    cell_comments = {}
    surface_comments = {}
    data_comments = {"Void": "Void Cell"}

    all_cells = {}
    all_surfaces = {}
    all_materials = {"Void": Material("m0"), "WIP": Material("m00")}
    all_options = {}

    def read_template(self, in_filename):
        """
        Reads from given filename to clean lines and create card objects for the app on launch
        :param in_filename: name of local file to read from
        :return: None
        """
        with open(in_filename, 'r') as f_read:
            curr_list = self.cell_line_pieces
            for line in f_read.readlines():
                if re.search(r'\bBegin Surfaces\b', line):
                    curr_list = self.surface_line_pieces
                elif re.search(r'\bBegin Options\b', line):
                    curr_list = self.data_line_pieces
                curr_list.append(line)

            self.file_title = self.cell_line_pieces.pop(0).strip()
            self.clean_comments(self.cell_line_pieces, self.cell_comments)
            self.clean_comments(self.surface_line_pieces, self.surface_comments)
            self.clean_comments(self.data_line_pieces, self.data_comments)

            self.join_card_pieces(self.cell_line_pieces, self.cell_lines)
            self.join_card_pieces(self.surface_line_pieces, self.surface_lines)
            self.join_card_pieces(self.data_line_pieces, self.data_lines)

            self.make_cards(self.cell_lines)
            self.make_cards(self.surface_lines)
            self.make_cards(self.data_lines)

            self.apply_comments(self.all_cells, self.cell_comments)
            self.apply_comments(self.all_surfaces, self.surface_comments)
            self.apply_comments(self.all_materials, self.data_comments)
        return


    @staticmethod
    def clean_comments(line_array, comment_array):
        """
        Performs reverse order search over line_array to find comments around cell/surface/material cards
        Assigns a comment to card number if used as a '$' comment on the same line as the card number or
        a 'cC' comment the line before. Prioritizes '$' comments over 'cC'
        :param line_array: Array of uncleaned MCNP lines
        :param comment_array: Dictionary to place new comments in
        :return: None
        """
        i = len(line_array)-1
        while 0 <= i:
            dollar_index = re.search(r'\$.*$', line_array[i])
            if dollar_index is not None:    # Find any '$' comments to save/delete
                if re.search(r'^m?\d{1,6}', line_array[i]) is not None:
                    new_comment = line_array[i][dollar_index.span()[0] + 1:].strip()
                    number_end = re.search(r'^m?\d{1,6}', line_array[i]).span()[1] + 1
                    number = line_array[i][0: number_end].strip()
                    comment_array[number] = new_comment
                    line_array[i] = line_array[i][: dollar_index.span()[0]]
                else:
                    line_array[i] = line_array[i][: dollar_index.span()[0]]
            if re.search(r'^[cC].*$', line_array[i]) is not None:   # Find any 'cC' comments to save/delete
                if re.search(r'^[cC][ \t]+\S.*$', line_array[i]) is not None:
                    if i < len(line_array) - 1 and re.search(r'^m?\d{1,6}', line_array[i+1]) is not None:
                        number_end = re.search(r'^m?\d{1,6}', line_array[i+1]).span()[1] + 1
                        number = line_array[i+1][0: number_end].strip()
                        if number[0] == "m":
                            number = number[1:]
                        if number not in comment_array:
                            comment_array[number] = line_array[i][2:].strip()
                line_array.pop(i)
                i -= 1
                continue
            if re.search(r'^[ \t]*\n+', line_array[i]) is not None:  # Finds blank line between 3 MCNP sections
                line_array.pop(i)
                i -= 1
                continue
            i -= 1
        return


    def join_card_pieces(self, line_pieces, line_array):
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

            start_line = line_pieces[index]
            if re.search(r'[ \t]*&', start_line):
                num_lines_continues = self._recurse_continue(line_pieces, index)
            elif len(line_pieces) - 1 > index:
                if re.search(r'^ {5,}\S+', line_pieces[index + 1]):
                    num_lines_continues = self._recurse_continue(line_pieces, index)

            for j in range(num_lines_continues + 1):
                result += line_pieces[index + j] + " "
            index += num_lines_continues
            result = result.replace("\n", "")  # remove \n
            result = re.sub(r'[ \t]{2,}', " ", result)  # remove extra spaces
            line_array.append(result)
            index += 1
        return

    def _recurse_continue(self, pieces, start_index, num=0):
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
            return self._recurse_continue(pieces, start_index, num + 1)
        elif space_index is not None:
            pieces[start_index + 1 + num] = pieces[start_index + 1 + num][space_index.span()[1] - 1:] + " "
            return self._recurse_continue(pieces, start_index, num + 1)
        else:
            print("Error: recurse_continue()")


    def make_cards(self, line_array):
        """
        Creates card objects from array of lines given by calling CardFactory
        :param line_array: Array of lines
        :return: None
        """
        factory = CardFactory()
        for line in line_array:
            made_card = factory.create_card(line)
            if isinstance(made_card, Cell):
                self.all_cells[made_card.number] = made_card
            elif isinstance(made_card, Surface):
                self.all_surfaces[made_card.number] = made_card
            elif isinstance(made_card, Material):
                self.all_materials[made_card.number] = made_card
            elif isinstance(made_card, Temperature):
                self.all_materials[made_card.number] = made_card
            elif isinstance(made_card, DataCard):
                self.all_options[made_card.number] = made_card
            else:
                continue
                #print(f"Card for {made_card} with line '{line}' not found")
        return


    @staticmethod
    def apply_comments(card_dict, comment_dict):
        """
        Applies comments to cards
        :param card_dict: Dictionary of MCNP card objects by number
        :param comment_dict: Dictionary of comments by number
        :return: None
        """
        for number in comment_dict:
            # number = number[re.search(r'^m?t?', number).span()[1]:]
            if number in card_dict:
                card_dict[number].set_comment(comment_dict[number])
        return


    def print_file(self, out_filename):
        """
        Prints card objects created to given filename
        :param out_filename: name of file to print to
        :return: out_filename
        """
        if out_filename == "" or out_filename is None:
            out_filename = '../mcnp_templates/test.i'

        with open(out_filename, 'w') as f_write:
            f_write.write(self.file_title + '\n')
            self.print_card(f_write, self.all_cells)
            print("\nc Begin Surface Cards:", file=f_write)
            self.print_card(f_write, self.all_surfaces)
            print("\nc Begin Data Cards:", file=f_write)
            self.print_card(f_write, self.all_materials)
            self.print_card(f_write, self.all_options)
        return out_filename

    @staticmethod
    def print_card(out_file, dictionary):
        """
        Helper method for print_file()
        :param out_file: Filestream to print to
        :param dictionary: Dictionary of things to print
        :return: None
        """
        for card in dictionary.values():
            if card.number == "0" or card.number == "00":
                continue
            print(card, file=out_file)
        return
