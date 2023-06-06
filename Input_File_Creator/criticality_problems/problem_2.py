from Input_File_Creator.input_file import *
from Input_File_Creator.mcnp_cards import *

input_file = InputFile("problem_2.txt", "pu_cylinder_radial_reflector")
all_cards = [
    CellCard(1, 1, -15.8, "-1 2 -3", "imp:n=1"),
    CellCard(2, 2, -18.8, "-4 -6 5 #1", "imp:n=1"),
    CellCard(3, 0, 0, "4:-5:6", "imp:n=0"),

    SurfaceCard(1, "cx", [4.935]),
    SurfaceCard(2, "px", [0]),
    SurfaceCard(3, "px", [6.909]),
    SurfaceCard(4, "cx", [9.935]),
    SurfaceCard(5, "px", [-5.0]),
    SurfaceCard(6, "px", [11.909]),

    Material("m1", [(94239, 1)]),
    Material("m2", [(92238, 0.992745), (92235, 0.007200)]),
    KCode(1000, 1.0, 15, 115),
    KSrc([[3.5, 0, 0]]),
]

for card in all_cards:
    input_file.addcard(card)
input_file.print_to_file()
