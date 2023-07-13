"""
Created by: Duncan Beauch
TEMPLATE FOR MCNP CARDS
"""

import re

from element_tools import zaid_to_isotope


class CardFactory:
    CELLS_REGEX = {
        'regular': re.compile(r' {0,6}^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\.?\d+(\.\d+)?[eE]?-?\d*[ \t]+[^a-zA-z]+[ \t]+[a-zA-z:,]+=.*$'),
        'void': re.compile(r'^ {0,6}\d{1,6}[ \t]+0[ \t][^a-zA-z]+[ \t]+[a-zA-z:,]+=.*$'),
        'like_but': re.compile(r'^ {0,6}\d{1,6}[ \t]+like[ \t]+\d{1,6}[ \t]but[ \t]+.+$')
    }

    SURFACES_REGEX = {
        'regular': re.compile(r'^ {0,6}\d+[ \t]+[^-\d\.]+[-\d\. \tr]+$'),
        'transform': re.compile(r'^ {0,6}\d+[ \t]+\d+[^-\d\.]+[-\d\. \tr]+$')
    }

    OPTIONS_REGEX = {
        'ksrc': re.compile(r'^ {0,6}ksrc[ \t]+((-?\d+(\.\d+)?[eE]?-?\d*[ \t]+){3})+$'),
        'transform': re.compile(r'^ {0,6}\*?(tr|TR)\d{1,6}[ \t]+(-?\d+\.?\d*[ \t]*)+$'),
        'mode': re.compile(r'^ {0,6}mode[ \t]+.+$'),
        'kcode': re.compile(r'^ {0,6}kcode[ \t]+.+$'),
        'prdmp': re.compile(r'^ {0,6}prdmp[ \t]+'),
        'print': re.compile(r'^ {0,6}print[ \t]+'),
        'F': re.compile(r'^ {0,6}[fF]\d+:[np][ \t]+'),
        'fq': re.compile(r'^ {0,6}fq\d+[ \t]+'),
        'fc': re.compile(r'^ {0,6}fc\d+[ \t]+'),
        'SD': re.compile(r'^ {0,6}SD\d+[ \t]+'),
        'FM': re.compile(r'^ {0,6}FM\d+[ \t]+'),
        'E': re.compile(r'^ {0,6}E\d+[ \t]+'),
        'FMESH': re.compile(r'^ {0,6}FMESH\d+:n[ \t]+'),
        'read': re.compile(r'^ {0,6}read file=.*'),
        'tmp': re.compile(r'^ {0,6}tmp[ \t]+'),
        'lost': re.compile(r'^ {0,6}lost[ \t]+'),
    }

    MATERIAL_TEMPERATURE_REGEX = {
        'material': re.compile(r'^ {0,6}m\d+[ \t]+(\d+(\.\d*)?c?[ \t]+-?\.?\d+(\.\d*)?([eE]-?\d+)?[ \t]*)+'),
        'temperature': re.compile(r'^ {0,6}mt\d{1,6}[ \t]+.+$')
    }

    def __init__(self, template):
        self.template = template

    def create_card(self, line, comment=""):
        if self.CELLS_REGEX['regular'].search(line):
            made_card = RegularCell(line.strip())
        elif self.CELLS_REGEX['void'].search(line):
            made_card = VoidCell(line.strip())
        elif self.CELLS_REGEX['like_but'].search(line):
            made_card = LikeCell(line.strip())
        elif self.SURFACES_REGEX['regular'].search(line):
            made_card = Surface(line.strip())
        elif self.SURFACES_REGEX['transform'].search(line):
            made_card = Surface(line.strip())
        elif self.MATERIAL_TEMPERATURE_REGEX['material'].search(line):
            made_card = Material(line.strip())
        elif self.MATERIAL_TEMPERATURE_REGEX['temperature'].search(line):
            made_card = Temperature(line.strip())
        elif self.OPTIONS_REGEX['transform'].search(line):
            made_card = Transform(line.strip())
        elif self.OPTIONS_REGEX['ksrc'].search(line):
            made_card = KSrc(line.strip())
        elif self.OPTIONS_REGEX['kcode'].search(line):
            made_card = KCode(line.strip())
        elif self.OPTIONS_REGEX['mode'].search(line):
            made_card = Mode(line.strip())
        else:
            matched = False
            for regex in self.OPTIONS_REGEX.values():
                search = regex.search(line)
                if search is not None:
                    start = search.span()[1]
                    made_card = Option(line.strip(), start)
                    matched = True
                    break
            if not matched:
                return None

        if isinstance(made_card, Cell):
            #   Add cell cards to universe
            if made_card.universe is not None:
                if made_card.universe not in self.template.all_universes:
                    self.template.all_universes[made_card.universe] = [made_card]
                else:
                    self.template.all_universes[made_card.universe].append(made_card)
            #   Add cell cards to fill dicts
            if made_card.fill is not None:
                for fill in made_card.fill:
                    if fill not in self.template.all_fills:
                        self.template.all_fills[fill] = [made_card]
                    else:
                        if made_card not in self.template.all_fills.get(fill):
                            self.template.all_fills[fill].append(made_card)

        made_card.set_comment(comment)
        return made_card


class Card:
    line_indent = "        "

    def __init__(self, comment=""):
        self.comment = comment

    def set_comment(self, comment):
        self.comment = f"{comment}"

    def get_inline_comment(self):
        if self.comment != "" and self.comment is not None:
            return f"\t\t$ {self.comment}"
        else:
            return ""

    def __str__(self):
        if self.comment != "" and self.comment is not None:
            return f"c {self.comment}\n"
        else:
            return ""


class Cell(Card):
    def __init__(self, line):
        #   Finds universe parameter
        u_param = re.search(r'u=\d+', line)
        if u_param is not None:
            self.universe = str(line[u_param.span()[0] + 2: u_param.span()[1] + 1].strip())
        else:
            self.universe = None

        # Finds fill parameters
        basic_fill_param = re.search(r'fill=\d+', line)
        complex_fill_param = re.search(r'fill=(((-?\d+:-?\d+[ \t]+){3}([ \t]*\d+r?)+))', line)
        if basic_fill_param is not None:
            self.fill = [line[basic_fill_param.span()[0] + 5: basic_fill_param.span()[1]].strip()]
        elif complex_fill_param is not None:
            ranges = re.search(r'fill=(((-?\d+:-?\d+[ \t]+){3}))', line)
            fills = line[ranges.span()[1]: complex_fill_param.span()[1]].strip().split()
            self.fill = []
            for f in fills:
                if 'r' in f:
                    continue  # Catches repeated fills: 200 '20r'
                if f in self.fill:
                    continue  # Catches if already in fill
                self.fill.append(f)
        else:
            self.fill = None

    def __str__(self):
        return super().__str__()

    def get_material(self):
        return self.material

    def get_density(self):
        return "Void" if isinstance(self, VoidCell) else self.density


class RegularCell(Cell):
    def __init__(self, line):
        super().__init__(line)
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        self.number = line[0: number_end].strip()

        material_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}', line).span()[1] + 1
        self.material = line[number_end: material_end].strip()

        density_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\.?\d+(\.\d+)?[eE]?-?\d*', line).span()[1] + 1
        self.density = line[material_end: density_end].strip()

        geom_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\.?\d+(\.\d+)?[eE]?-?\d*[ \t]+[^a-zA-z]+', line).span()[1]
        self.geom = line[density_end: geom_end].strip()

        self.param = line[geom_end:].strip()

        self.children = []

    def __str__(self):
        printed_geom = re.sub(r'\)[ \t]+\(', f")\n{self.line_indent}(", self.geom)
        printed_geom = re.sub(r':[ \t]+\(', f":\n{self.line_indent}(", printed_geom)
        digit_parenth = re.search(r'\d[ \t]+\(', printed_geom)
        if digit_parenth is not None:
            printed_geom = printed_geom[:digit_parenth.span()[0] + 1] + f"\n{self.line_indent}" + printed_geom[
                                                                                             digit_parenth.span()[
                                                                                                 0] + 2:]
        parts = self.param.split()
        printed_param = f'\n{self.line_indent}'.join([' '.join(parts[i:i + 5]) + self.line_indent for i in range(0, len(parts), 5)])
        printed_param = printed_param[:re.search(r'\s+$', printed_param).span()[0]]
        return f"{self.number}\t{self.material}\t{self.density}{self.get_inline_comment()}\n{self.line_indent}{printed_geom}\n{self.line_indent}{printed_param}"


class VoidCell(Cell):
    def __init__(self, line):
        super().__init__(line)
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        self.number = line[0: number_end].strip()

        material_end = re.search(r'^\d{1,6}[ \t]+0', line).span()[1] + 1
        self.material = line[number_end: material_end].strip()

        self.density = 0

        geom_end = re.search(r'^\d{1,6}[ \t]+0[ \t][^a-zA-z]+', line).span()[1]
        self.geom = line[material_end: geom_end].strip()

        self.param = line[geom_end:].strip()

        self.children = []

    def __str__(self):
        printed_geom = re.sub(r'\)[ \t]+\(', f")\n{self.line_indent}(", self.geom)
        printed_geom = re.sub(r':[ \t]+\(', f":\n{self.line_indent}(", printed_geom)
        digit_par = re.search(r'\d[ \t]+\(', printed_geom)
        if digit_par is not None:
            printed_geom = printed_geom[:digit_par.span()[0] + 1] + f"\n{self.line_indent}" + printed_geom[
                                                                                         digit_par.span()[0] + 2:]
        return f"{self.number}\t{self.material}{self.get_inline_comment()}\n{self.line_indent}{printed_geom}\n{self.line_indent}{self.param}"


class LikeCell(Cell):
    def __init__(self, line):
        super().__init__(line)
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        self.number = line[0: number_end].strip()

        like_end = re.search(r'^\d{1,6}[ \t]+like', line).span()[1] + 1
        origin_cell_end = re.search(r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}', line).span()[1] + 1
        self.origin_cell = line[like_end: origin_cell_end].strip()

        but_end = re.search(r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}[ \t]+but', line).span()[1] + 1
        self.changes = line[but_end:].strip()

        self.material = ""
        self.density = ""
        self.geom = ""
        self.param = ""

    def __str__(self):
        parts = self.changes.split()
        # Print changes with newlines every 5 spaces
        printed_changes = f'\n {self.line_indent}'.join([' '.join(parts[i:i + 5]) for i in range(0, len(parts), 5)])
        return f"{self.number} like {self.origin_cell} but {printed_changes}\t{self.get_inline_comment()}"


class Surface(Card):
    def __init__(self, line):
        number_end = re.search(r'^\d+', line).span()[1] + 1
        self.number = line[: number_end].strip()

        if re.search(r'^\d+[ \t]+\d+[^-\d\.]+[-\d\. \tr]+$', line):  # Surface with associated transform
            transform_end = re.search(r'^\d+[ \t]+\d+', line).span()[1] + 1
            self.transform = line[number_end: transform_end].strip()

            mnemonic_end = re.search(r'^\d+[ \t]+\d+[^-\d\.]+', line).span()[1]
            self.mnemonic = line[transform_end: mnemonic_end].strip()

        else:
            self.transform = ""
            mnemonic_end = re.search(r'^\d+[ \t]+[^-\d\.]+', line).span()[1]
            self.mnemonic = line[number_end: mnemonic_end].strip()

        self.dimensions = line[mnemonic_end:].strip()

    def __str__(self):
        return f"{self.number}\t{self.transform}\t{self.mnemonic}\t{self.dimensions}{self.get_inline_comment()}"


class DataCard(Card):
    def __str__(self):
        return super().__str__()


class KCode(DataCard):
    def __init__(self, line):
        self.number = "kcode"
        self.param = line[5:].strip()
        # self.nsrck = " "
        # self.rkk = " "
        # self.ikz = " "
        # self.kct = " "

    def __str__(self):
        return f"{super().__str__()}kcode\t{self.param}"  # {self.nsrck}\t{self.rkk}\t{self.ikz}\t{self.kct}"


class KSrc(DataCard):
    def __init__(self, line):
        self.number = "ksrc"
        self.locations = []
        ksrc_end = re.search(r'^ksrc', line).span()[1] + 1
        source_list = re.split(r'[ \t]+', line[ksrc_end:].strip())
        for i in range(int(len(source_list) / 3)):
            self.locations.append((source_list[3 * i], source_list[3 * i + 1], source_list[3 * i + 2]))
        self.comment = ""

    def __str__(self):
        locations_str = ""
        locations_str = '\n'.join([f"{self.line_indent}{triplet[0]}  {triplet[1]}  {triplet[2]}" for triplet in self.locations])
        return f"{super().__str__()}ksrc{locations_str}"


class Material(DataCard):
    def __init__(self, line):
        self.zaid_fracs = []
        number_end = re.search(r'^m\d+', line).span()[1] + 1
        self.number = line[1: number_end].strip()

        zaid_list = re.split(r'[ \t]+', line[number_end:].strip())
        for i in range(int(len(zaid_list) / 2)):
            self.zaid_fracs.append((zaid_list[2 * i], zaid_list[2 * i + 1]))
        self.comment = ""

    def __str__(self, comments_on):
        zaid_fracs_str = '\n'.join([
            f"{self.line_indent}{pair[0]}\t{pair[1]}" + (f"    \t$ {zaid_to_isotope(pair[0])}" if comments_on else "")
            for pair in self.zaid_fracs
        ])
        return f"{super().__str__()}m{self.number}{zaid_fracs_str}"


class Temperature(DataCard):
    def __init__(self, line):
        number_end = re.search(r'^mt\d{1,6}[ \t]+', line).span()[1]
        self.number = line[1: number_end].strip()
        self.param = line[number_end:]

    def __str__(self):
        return f"{super().__str__()}m{self.number}\t\t{self.param}"


class Mode(DataCard):
    def __init__(self, line):
        self.number = "mode"
        self.param = line[4:].strip()

    def __str__(self):
        return f"{super().__str__()}mode\t{self.param}"


class Transform(DataCard):
    def __init__(self, line):
        number_end = re.search(r'^\*?(tr|TR)\d{1,6}[ \t]+', line).span()[1]
        self.number = line[: number_end].strip()
        self.param = line[number_end:]

    def __str__(self):
        return f"{super().__str__()}{self.number}\t{self.param}"


class Option(DataCard):
    def __init__(self, line, start):
        self.number = line[:start].strip()
        self.param = line[start:].strip()

    def __str__(self):
        parts = self.param.split()
        printed_param = "\n".join([self.line_indent + ' '.join(parts[i:i + 5]) for i in range(0, len(parts), 5)])
        return f"{self.number}{self.get_inline_comment()}{printed_param}"
