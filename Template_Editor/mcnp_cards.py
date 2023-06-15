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


class Cell:
    def __init__(self, number, material, density, geom, param=""):
        self.number = number
        self.material = material
        self.density = density
        self.geom = geom
        self.param = param
        if material == 0:
            self.density = "\t"
        self.universe = 0

    def __str__(self):
        return f"{self.number}\t{self.material}\t{self.density}\t{self.geom}\t{self.param}"

    def get_material(self):
        return "Void" if self.material == "0" else self.material

    def get_density(self):
        return "Void" if self.density == "\t" else self.density


class LikeCell(Cell):
    def __init__(self, number, related_cell, changes):
        self.number = number
        self.related_cell = related_cell
        self.changes = changes

    def __str__(self):
        return f"{self.number} like {self.related_cell} but {self.changes}"


class Surface:
    def __init__(self, number, mnemonic, dimensions):
        self.number = number
        self.mnemonic = mnemonic
        self.dimensions = dimensions

    def __str__(self):
        dimensions_str = ' '.join(str(num) for num in self.dimensions)
        return f"{self.number}\t{self.mnemonic}\t{dimensions_str}"


class DataCard:
    pass


class KCode(DataCard):
    def __init__(self, nsrck, rkk, ikz, kct):
        self.name = "kcode"
        self.nsrck = nsrck
        self.rkk = rkk
        self.ikz = ikz
        self.kct = kct

    def __str__(self):
        return f"{self.name}\t{self.nsrck}\t{self.rkk}\t{self.ikz}\t{self.kct}"


class KSrc(DataCard):
    def __init__(self, locations):
        self.name = "ksrc"
        self.locations = locations

    def __str__(self):
        locations_str = '\t'.join(' '.join(map(str, location)) for location in self.locations)
        return f"{self.name}\t{locations_str}"


class Material(DataCard):
    def __init__(self, number, zaid_fracs):
        self.number = number
        self.zaid_fracs = zaid_fracs

    def __str__(self):
        zaid_fracs_str = '\t'.join(' '.join(map(str, zaid_frac)) for zaid_frac in self.zaid_fracs)
        return f"m{self.number}\t\t{zaid_fracs_str}"


class Temperature(DataCard):
    def __init__(self, number, params):
        self.number = number
        self.params = params

    def __str__(self):
        return f"mt{self.number}\t\t{self.params}"


class Mode(DataCard):
    def __init__(self, _mode):
        self._mode = _mode

    def __str__(self):
        return f"mode {self._mode}"


class Transform(DataCard):
    def __init__(self, param):
        self.param = param

    def __str__(self):
        return f"*tr {self.param}"


class Option(DataCard):
    def __init__(self, code, params):
        self.code = code
        self.params = params

    def __str__(self):
        return f"{self.code}\t{self.params}"
