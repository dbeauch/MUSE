from input_file import *
from mcnp_cards import *

# Default File
default_input = InputFile("default.txt", "")
default_input.print_to_file()

input_file = InputFile
all_cards = [

]

for card in all_cards:
    input_file.addcard(card)
input_file.print_to_file()
