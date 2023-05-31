from input_file import *
from mcnp_cards import *

input_file = InputFile()
all_cards = [

]

for card in all_cards:
    input_file.addcard(card)
input_file.print_to_file()
