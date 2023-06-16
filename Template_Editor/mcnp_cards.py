"""
Created by: Duncan Beauch
TEMPLATE FOR MCNP CARDS

CellCard(number, material number, density, geom string, optional param string)
    CellCard(, , , "", "")

SurfaceCard(number, mnemonic, array of numbers)
    SurfaceCard(, "", [])

KCode(nsrck neutrons per cycle, rkk initial keff guess, ikz cycles skipped, kct cycles to run)
    KCode(, , , )

KSrc(array of arrays representing x-y-z locations)
    KSrc([[, , ]])

Material(number, array of tuples for each zaid-fraction pair)
    Material("", [(, )])

Moderator(number, params)
    Moderator("", "")
"""
import re


class CardFactory:
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

    # _end = re.search(r'', line).span()[1] + 1
    # = line[_end: _end].strip()
    def create_card(self, line):
        if re.search(self.CELLS_REGEX['regular'], line):
            made_card = Cell(line)
        elif re.search(self.CELLS_REGEX['void'], line):
            made_card = VoidCell(line)
        elif re.search(self.CELLS_REGEX['like_but'], line):
            made_card = LikeCell(line)
        elif re.search(self.SURFACES_REGEX['regular'], line):
            made_card = Surface(line)
        elif re.search(self.SURFACES_REGEX['transform'], line):
            made_card = Surface(line)
        elif re.search(self.MATERIAL_TEMPERATURE_REGEX['material'], line + " "):
            made_card = Material(line)
        elif re.search(self.MATERIAL_TEMPERATURE_REGEX['temperature'], line):
            made_card = Temperature(line)
        elif re.search(self.OPTIONS_REGEX['transform'], line):
            made_card = Transform(line)
        elif re.search(self.OPTIONS_REGEX['ksrc'], line):
            made_card = KSrc(line)
        elif re.search(self.OPTIONS_REGEX['kcode'], line):
            made_card = KCode(line)
        elif re.search(self.OPTIONS_REGEX['mode'], line):
            made_card = Mode(line)
        else:
            made_card = None
            print(f"Card for {line} not found")
        return made_card


class Card:
    pass


class Cell(Card):
    def __init__(self, line):
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        self.number = line[0: number_end].strip()

        material_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}', line).span()[1] + 1
        self.material = line[number_end: material_end].strip()

        density_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\d+(\.\d+)?[eE]?-?\d*', line).span()[1] + 1
        self.density = line[material_end: density_end].strip()

        geom_end = re.search(r'^\d{1,6}[ \t]+[1-9]\d{0,6}[ \t]+-?\d+(\.\d+)?[eE]?-?\d*[ \t]+[^a-zA-z]+', line).span()[1]
        self.geom = line[density_end: geom_end].strip()

        self.param = line[geom_end:].strip()


    def __str__(self):
        return f"{self.number}\t{self.material}\t{self.density}\t{self.geom}\t{self.param}"

    def get_material(self):
        return "Void" if isinstance(self, VoidCell) else self.material

    def get_density(self):
        return "Void" if isinstance(self, VoidCell) else self.density


class VoidCell(Cell):
    def __init__(self, line):
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        self.number = line[0: number_end].strip()

        material_end = re.search(r'^\d{1,6}[ \t]+0', line).span()[1] + 1
        self.material = line[number_end: material_end].strip()

        self.density = 0

        geom_end = re.search(r'^\d{1,6}[ \t]+0[ \t][^a-zA-z]+', line).span()[1]
        self.geom = line[material_end: geom_end].strip()

        self.param = line[geom_end:].strip()


    def __str__(self):
        return f"{self.number}\t{self.material}\t\t\t{self.geom}\t{self.param}"



class LikeCell(Cell):
    def __init__(self, line):
        number_end = re.search(r'^\d{1,6}', line).span()[1] + 1
        self.number = line[0: number_end].strip()

        like_end = re.search(r'^\d{1,6}[ \t]+like', line).span()[1] + 1
        related_cell_end = re.search(r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}', line).span()[1] + 1
        self.related_cell = line[like_end: related_cell_end].strip()

        but_end = re.search(r'^\d{1,6}[ \t]+like[ \t]+\d{1,6}[ \t]+but', line).span()[1] + 1
        self.changes = line[but_end:].strip()



    def __str__(self):
        return f"{self.number} like {self.related_cell} but {self.changes}"


class Surface(Card):
    def __init__(self, line):
        self.number = " "
        self.mnemonic = " "
        self.dimensions = " "

    def __str__(self):
        dimensions_str = ' '.join(str(num) for num in self.dimensions)
        return f"{self.number}\t{self.mnemonic}\t{dimensions_str}"


class DataCard(Card):
    pass


class KCode(DataCard):
    def __init__(self, line):
        self.name = "kcode"
        self.nsrck = " "
        self.rkk = " "
        self.ikz = " "
        self.kct = " "

    def __str__(self):
        return f"{self.name}\t{self.nsrck}\t{self.rkk}\t{self.ikz}\t{self.kct}"


class KSrc(DataCard):
    def __init__(self, line):
        self.name = " "
        self.locations = " "

    def __str__(self):
        locations_str = '\t'.join(' '.join(map(str, location)) for location in self.locations)
        return f"{self.name}\t{locations_str}"


class Material(DataCard):
    def __init__(self, line):
        self.zaid_fracs = []
        number_end = re.search(r'^m\d+', line).span()[1] + 1
        self.number = line[1: number_end].strip()

        zaid_list = re.split(r'[ \t]+', line[number_end:].strip())
        for i in range(int(len(zaid_list) / 2)):
            self.zaid_fracs.append((zaid_list[2 * i], zaid_list[2 * i + 1]))

    def __str__(self):
        zaid_fracs_str = '\t'.join(' '.join(map(str, zaid_frac)) for zaid_frac in self.zaid_fracs)
        return f"m{self.number}\t\t{zaid_fracs_str}"


class Temperature(DataCard):
    def __init__(self, line):
        self.number = " "
        self.param = " "

    def __str__(self):
        return f"mt{self.number}\t\t{self.param}"


class Mode(DataCard):
    def __init__(self, line):
        self._mode = " "

    def __str__(self):
        return f"mode {self._mode}"


class Transform(DataCard):
    def __init__(self, line):
        self.param = " "

    def __str__(self):
        return f"*tr {self.param}"


class Option(DataCard):
    def __init__(self, line):
        self.code = " "
        self.param = " "

    def __str__(self):
        return f"{self.code}\t{self.param}"
