from input_file import *
from mcnp_cards import *

# Default File
default_input = InputFile("default.txt")
default_input.print_to_file()

input1 = InputFile("input1.txt", "Jezebel problem. Bare plutonium sphere with nickel shell")

input1.addcard(CellCard(1, 1, 4.0290e-2, -1, "imp:n=1"))
input1.addcard(SurfaceCard(1, "so", 6.38493))
input1.addcard(KCode(1000, 1.0, 15, 115))

input1.print_to_file()
