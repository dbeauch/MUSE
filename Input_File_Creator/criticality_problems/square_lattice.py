from Input_File_Creator.input_file import *
from Template_Editor.mcnp_cards import *

input_file = InputFile("square_lattice.txt", "Test of Square Lattice Card")

lattice = SquareLattice(3, 2, 17.79, f"0:2 0:1 0:0\t0 1 1 0 1 0")

all_cards = [
    CellCard(1, 1, 9.9270e-2, "-1 5 -6", "u=1 imp:n=1"),
    CellCard(2, 0, 0, "-1 6 -7", "u=1 imp:n=1"),
    CellCard(3, 2, 8.6360e-2, "-2 #1 #2", "u=1 imp:n=1"),
    CellCard(4, 0, 0, "2", "u=1 imp:n=1"),

    CellCard(7, 0, 0, lattice.outside, "imp:n=0"),

    SurfaceCard(1, "cz", [12.49]),
    SurfaceCard(2, "cz", [12.79]),
    SurfaceCard(5, "pz", [0.0]),
    SurfaceCard(6, "pz", [39.24]),
    SurfaceCard(7, "pz", [101.7]),

    lattice,

    KCode(1000, 1.0, 15, 115),
    KSrc([[0, 0, 19.62], [35.58, 0, 19.62], [71.16, 0, 19.62], [0, 35.58, 19.62], [35.58, 35.58, 19.62], [71.16, 35.58, 19.62]]),
    Material("m1", [(1001, 6.0070e-2), (8016, 3.6540e-2), (7014, 2.3699e-3), (94239, 2.7682e-4), (94240, 1.2214e-5), (94241, 8.3390e-7), (94242, 4.5800e-8)]),
    Moderator("mt1", "lwtr"),
    Material("m2", [(26000, 6.3310e-2), (24000, 1.6540e-2), (28000, 6.5100e-3)]),
]

for card in all_cards:
    input_file.addcard(card)
input_file.print_to_file()
