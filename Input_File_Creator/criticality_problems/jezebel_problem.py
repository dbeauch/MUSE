from Input_File_Creator.input_file import *
from Input_File_Creator.mcnp_cards import *

input = InputFile("jezebel.txt", "Jezebel problem. Bare plutonium sphere with nickel shell")
all_cards = [
    CellCard(1, 1, 4.0290e-2, [-1], "imp:n=1"),
    CellCard(2, 2, 9.1322e-2, [1, -2], "imp:n=1"),
    CellCard(3, 0, 0, [2], "imp:n=0"),

    SurfaceCard(1, "so", [6.38493]),
    SurfaceCard(2, "so", [6.39763]),

    KCode(1000, 1.0, 15, 115),
    KSrc([[0, 0, 0]]),
    Material("m1", [(94239, 3.7047e-2), (94240, 1.751e-3), (94241, 1.17e-4), (31000, 1.375e-3)]),
    Material("m2", [(28000, 1.0)]),
]

for card in all_cards:
    input.addcard(card)
input.print_to_file()