#########################################################################################################
#                                      Created by: Duncan Beauch                                        #
#                                       TEMPLATE FOR MCNP CARDS                                         #
#                                                                                                       #
#       CellCard(number, material number, density, geom string, optional param string)                  #
#                                           CellCard(, , , "", "")                                      #
#                                                                                                       #
#       SurfaceCard(number, mnemonic, array of numbers)                                                 #
#                                           SurfaceCard(, "", [])                                       #
#                                                                                                       #
#       KCode(nsrck neutrons per cycle, rkk initial keff guess, ikz cycles skipped, kct cycles to run)  #
#                                             KCode(, , , )                                             #
#                                                                                                       #
#       KSrc(array of arrays representing x-y-z locations)                                              #
#                                             KSrc([[, , ]])                                            #
#                                                                                                       #
#       Material(name, array of tuples for each zaid-fraction pair)                                     #
#                                            Material("", [(, )])                                       #
#                                                                                                       #
#       Moderator(name, material identifier)                                                            #
#                                             Moderator("", "")                                         #
#########################################################################################################
from decimal import Decimal

# Global static section
global curr_number
curr_number = 99999


def get_number():
    global curr_number
    result = curr_number
    curr_number -= 1
    return result


class CellCard:
    def __init__(self, number, material, density, geom, params=""):
        self.number = number
        self.material = material
        self.density = density
        self.geom = geom
        self.params = params
        if material == 0:
            self.density = "\t"
        self.universe = 0

    def __str__(self):
        return f"{self.number}\t{self.material}\t{self.density}\t{self.geom}\t{self.params}"


class SurfaceCard:
    def __init__(self, number, mnemonic, dimensions):
        self.number = number
        self.mnemonic = mnemonic
        self.dimensions = dimensions

    def __str__(self):
        result = f"{self.number}\t{self.mnemonic}\t"
        for num in self.dimensions:
            result += f"{num} "
        return result


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
    # location expected as a list length 3
    def __init__(self, locations):
        self.name = "ksrc"
        self.locations = locations

    def __str__(self):
        result = f"{self.name}\t"
        for location in self.locations:
            result += f"{location[0]} {location[1]} {location[2]}\t"
        return result


class Material(DataCard):
    # zaid_frac expected as a tuple: (zaid, fraction)
    def __init__(self, mname, zaid_fracs):
        self.mname = mname
        self.zaid_fracs = zaid_fracs

    def __str__(self):
        result = f"{self.mname}\t\t"
        for zaid_frac in self.zaid_fracs:
            result += f"{zaid_frac[0]} {zaid_frac[1]}\t"
        return result


class Moderator(DataCard):
    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier

    def __str__(self):
        return f"{self.name}\t\t{self.identifier}"


class SquareLattice:
    def __init__(self, rows, cols, radius, filler):
        self.rows = rows
        self.cols = cols
        self.radius = Decimal(f"{radius}")
        self.filler = filler

        # Lattice Initial Settings
        # no z_ceiling
        z_floor = -1.0
        window_truncation = Decimal(f"0.01")

        self.surfaces = []
        # Planes defining element (0, 0, 0)
        boundary1 = SurfaceCard(get_number(), "px", [self.radius])  # positive x
        boundary2 = SurfaceCard(get_number(), "px", [-self.radius])  # negative x
        boundary3 = SurfaceCard(get_number(), "py", [self.radius])  # positive y
        boundary4 = SurfaceCard(get_number(), "py", [-self.radius])  # negative y
        self.surfaces.append(boundary1)
        self.surfaces.append(boundary2)
        self.surfaces.append(boundary3)
        self.surfaces.append(boundary4)

        # Planes defining edge of lattice
        window0 = SurfaceCard(get_number(), "pz", [z_floor])
        window1 = SurfaceCard(get_number(), "px", [self.radius * (rows * 2 - 1) - window_truncation])
        window2 = SurfaceCard(get_number(), "px", [-(self.radius - window_truncation)])
        window3 = SurfaceCard(get_number(), "py", [self.radius * (cols * 2 - 1) - window_truncation])
        window4 = SurfaceCard(get_number(), "py", [-(self.radius - window_truncation)])
        self.surfaces.append(window0)
        self.surfaces.append(window1)
        self.surfaces.append(window2)
        self.surfaces.append(window3)
        self.surfaces.append(window4)

        self.cells = []
        self.lat_universe = get_number()
        lat_cell = CellCard(get_number(), 0, 0,
                            f"-{boundary1.number} {boundary2.number} -{boundary3.number} {boundary4.number}",
                            f"lat={get_number()}\tfill={self.filler}\tu={self.lat_universe}\timp:n=1\t$ lattice")
        window_cell = CellCard(get_number(), 0, 0, f"{window0.number} -{window1.number} {window2.number} -{window3.number} {window4.number}",
                               f"fill={self.lat_universe}\timp:n=1\t$ window")
        self.cells.append(lat_cell)
        self.cells.append(window_cell)

        self.outside = f"{window1.number}:-{window2.number}:{window3.number}:-{window4.number}:-{window0.number}"


    def __str__(self):
        return f"This shouldn't print to file but its the SquareLattice universe number {self.lat_universe}"
