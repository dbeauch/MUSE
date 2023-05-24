class CellCard:
    def __init__(self, number, material, density, geom, params=""):
        self.number = number
        self.material = material
        self.density = density
        self.geom = geom
        self.params = params

    def __str__(self):
        return f"{self.number} {self.material} {self.density} {self.geom} {self.params}"


class SurfaceCard:
    def __init__(self, number, mnemonic, dimensions):
        self.number = number
        self.mnemonic = mnemonic
        self.dimensions = dimensions

    def __str__(self):
        return f"{self.number} {self.mnemonic} {self.dimensions}"


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
        return f"{self.name} {self.nsrck} {self.rkk} {self.ikz} {self.kct}"


class KSrc(DataCard):
    # location expected as a list length 3
    def __init__(self, name, locations):
        self.name = "ksrc"
        self.locations = locations

    def __str__(self):
        result = f"{self.name}"
        for location in self.locations:
            result += f"{location[0]} {location[1]} {location[2]} "
        return result


class Material(DataCard):
    # zaid_frac expected as a tuple: (zaid, fraction)
    def __init__(self, name, number, zaid_fracs):
        self.name = name
        self.number = number
        self.zaid_fracs = zaid_fracs

    def __str__(self):
        result = f"{self.name}{self.number} "
        for zaid_frac in self.zaid_fracs:
            result += f"{zaid_frac[0]}{zaid_frac[1]}"
