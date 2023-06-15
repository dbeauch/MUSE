import re
from mcnp_cards import *


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class TemplateHandler(Singleton):
    CELLS_REGEX = {
        'regular': r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\d+(\.\d+)?[eE]?-?\d*[ \t]+[^a-zA-z]+[ \t]+[a-zA-z]+=.*$',
        'void': r'^\d{1,6}[ \t]+0[ \t][^a-zA-z]+[ \t]+[a-zA-z]+=.*$',
        'like_but': r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}[ \t]but[ \t]+.+$'
    }

    SURFACES_REGEX = {
        'regular': r'^\d+[ \t]+[^-\d\.]+[^a-zA-Z]+$',
        'transform': r'^\d+[ \t]+\d+[^-\d\.]+[^a-zA-Z]+$'
    }

    OPTIONS_REGEX = {
        'mode': r'^mode[ \t]+\.+$',
        'kcode': r'^kcode[ \t]+\.+$',
        'ksrc': r'ksrc[ \t]+((-?\d+(\.\d+)?[eE]?-?\d*[ \t]+){3})+$',
        'transform': r''
    }

    MATERIAL_TEMPERATURE_REGEX = {
        'material': r'^m\d+[ \t]+(\d+(\.\S+)?[ \t]+-?\.?\d+(\.\d+)?[eE]?-?\d*[ \t]+)+$',
        'temperature': r''
    }

    file_title = ""
    cell_line_pieces = []
    surface_line_pieces = []
    data_line_pieces = []

    cell_lines = []
    surface_lines = []
    data_lines = []

    all_cells = {}
    all_like_cells = {}
    all_surfaces = {}
    all_materials = {}
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
            self.clean_pieces(self.cell_line_pieces)
            self.clean_pieces(self.surface_line_pieces)
            self.clean_pieces(self.data_line_pieces)

            self.join_card_pieces(self.cell_line_pieces, self.cell_lines)
            self.join_card_pieces(self.surface_line_pieces, self.surface_lines)
            self.join_card_pieces(self.data_line_pieces, self.data_lines)

            self.make_cards(self.cell_lines)
            self.make_cards(self.surface_lines)
            self.make_cards(self.data_lines)
            self.all_materials[0] = 0
        return

    @staticmethod
    def clean_pieces(array):
        """
        Cleans each entry of array parameter; removes $ comments and C/c comments
        :param array: array to be cleaned
        :return: None
        """
        i = 0
        while i < len(array):
            comment_index = re.search(r'[ \t]*\$', array[i])  # remove $ comment along with leading white space
            if comment_index is not None:
                array[i] = array[i][0: comment_index.span()[0]]
            if re.search(r'^[ \t]{0,5}[cC]\s', array[i]) is not None:  # remove 'c' comments
                array.pop(i)
                i -= 1
            i += 1
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
                num_lines_continues = self.recurse_continue(line_pieces, index)
            elif len(line_pieces) - 1 > index:
                if re.search(r'^ {5,}\S+', line_pieces[index + 1]):
                    num_lines_continues = self.recurse_continue(line_pieces, index)

            for j in range(num_lines_continues + 1):
                result += line_pieces[index + j] + " "
            index += num_lines_continues
            result = result.replace("\n", "")  # remove \n
            result = re.sub(r'[ \t]{2,}', " ", result)  # remove extra spaces
            line_array.append(result)
            index += 1
        return

    def recurse_continue(self, pieces, start_index, num=0):
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
            return self.recurse_continue(pieces, start_index, num + 1)
        elif space_index is not None:
            pieces[start_index + 1 + num] = pieces[start_index + 1 + num][space_index.span()[1] - 1:] + " "
            return self.recurse_continue(pieces, start_index, num + 1)
        else:
            print("Error: recurse_continue()")

    def make_cards(self, line_array):
        """
        Creates card objects from array of lines given
        :param line_array: Array of lines
        :return: None
        """
        for line in line_array:
            if re.search(self.CELLS_REGEX['regular'], line):
                made_card = self.make_cell(line)
                self.all_cells[made_card.number] = made_card
            elif re.search(self.CELLS_REGEX['void'], line):
                made_card = self.make_void_cell(line)
                self.all_cells[made_card.number] = made_card
            elif re.search(self.CELLS_REGEX['like_but'], line):
                made_card = self.make_like_but_cell(line)
                self.all_cells[made_card.number] = made_card
            # elif re.search(self.SURFACES_REGEX['regular'], line):
            #     made_card = self.make_surface(line)
            #     self.all_surfaces[made_card.number] = made_card
            # elif re.search(self.SURFACES_REGEX['transform'], line):
            #     made_card = self.make_transform_surface(line)
            #     self.all_surfaces[made_card.number] = made_card
            elif re.search(self.MATERIAL_TEMPERATURE_REGEX['material'], line):
                made_card = self.make_material(line)
                self.all_materials[made_card.number] = made_card
            # elif re.search(self.MATERIAL_TEMPERATURE_REGEX['temperature'], line):
            #     made_card = self.make_temperature(line)
            #     self.all_temperatures[made_card.number] = made_card
            # else:
            #     for option in self.OPTIONS_REGEX.keys():
            #         if re.search(self.OPTIONS_REGEX[option], line):
            #             made_card = self.make_option(line, option)
            #             self.all_options[made_card.number] = made_card
        return

    # _end = re.search(r'', line).span()[1] + 1
    # = line[_end: _end].strip()
    @staticmethod
    def make_cell(line):
        """
        Helper method for make_cards(). Creates a mcnp_card object from line
        :param line: string containing mcnp input line
        :return: mcnp_card object
        """
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        number = line[0: number_end].strip()

        material_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}', line).span()[1] + 1
        material = line[number_end: material_end].strip()

        density_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\d+(\.\d+)?[eE]?-?\d*', line).span()[1] + 1
        density = line[material_end: density_end].strip()

        geom_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\d+(\.\d+)?[eE]?-?\d*[ \t]+[^a-zA-z]+', line).span()[1]
        geom = line[density_end: geom_end].strip()

        params = line[geom_end:].strip()

        return Cell(number, material, density, geom, params)

    @staticmethod
    def make_void_cell(line):
        """
        Helper method for make_cards(). Creates a mcnp_card object from line
        :param line: string containing mcnp input line
        :return: mcnp_card object
        """
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        number = line[0: number_end].strip()

        material_end = re.search(r'^\d{1,6}[ \t]+0', line).span()[1] + 1
        material = line[number_end: material_end].strip()

        geom_end = re.search(r'^\d{1,6}[ \t]+0[ \t][^a-zA-z]+', line).span()[1]
        geom = line[material_end: geom_end].strip()

        params = line[geom_end:].strip()

        return Cell(number, material, "\t", geom, params)

    @staticmethod
    def make_like_but_cell(line):
        """
        Helper method for make_cards(). Creates a mcnp_card object from line
        :param line: string containing mcnp input line
        :return: mcnp_card object
        """
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        number = line[0: number_end].strip()

        like_end = re.search(r'^\d{1,6}[ \t]+like', line).span()[1] + 1

        related_cell_end = re.search(r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}', line).span()[1] + 1
        related_cell = line[like_end: related_cell_end].strip()

        but_end = re.search(r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}[ \t]+but', line).span()[1] + 1

        changes = line[but_end:].strip()

        return LikeCell(number, related_cell, changes)

    # ^m\d+[ \t]+(\d+[ \t]+-?\d+(\.\d+)?[eE]?-?\d*[ \t]+)+
    @staticmethod
    def make_material(line):
        """
        Helper method for make_cards(). Creates a mcnp_card object from line
        :param line: string containing mcnp input line
        :return: mcnp_card object
        """
        zaid_fracs = []
        number_end = re.search(r'^m\d+', line).span()[1] + 1
        number = line[1: number_end].strip()

        zaid_list = re.split(r'[ \t]+', line[number_end:].strip())
        for i in range(int(len(zaid_list) / 2)):
            zaid_fracs.append((zaid_list[2 * i], zaid_list[2 * i + 1]))

        return Material(number, zaid_fracs)

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
            self.print_card(f_write, self.all_like_cells)
            print("\nc Begin Surface Cards:", file=f_write)
            self.print_card(f_write, self.all_surfaces)
            print("\nc Begin Data Cards:", file=f_write)
            self.print_card(f_write, self.all_materials)
            self.print_card(f_write, self.all_options)
        return out_filename

    @staticmethod
    def print_card(out_file, dictionary):
        for card in dictionary.values():
            print(card, file=out_file)
        return
