#########################################################################################################
#                                        Created by: Duncan Beauch                                      #
#                                         TEMPLATE FOR MCNP CARDS                                       #
#                                                                                                       #
#       CellCard(number, material number, density, array of geom, optional param string)                #
#                                           CellCard(, , , [], "")                                      #
#                                                                                                       #
#       SurfaceCard(number, mnemonic, array of numbers)                                                 #
#                                           SurfaceCard(, , [])                                         #
#                                                                                                       #
#       KCode(nsrck neutrons per cycle, rkk initial keff guess, ikz cycles skipped, kct cycles to run)  #
#                                              KCode(, , , )                                            #
#                                                                                                       #
#       KSrc(array of arrays representing x-y-z locations)                                              #
#                                              KSrc([[, , ]])                                           #
#       Material(name, array of tuples for each zaid-fraction pair)                                     #
#                                            Material(, [(, )])                                         #
#                                                                                                       #
#########################################################################################################
from input_file import *
from mcnp_cards import *

# Default File
default_input = InputFile("default.txt")
default_input.print_to_file()


input1 = InputFile("input1.txt", "Jezebel problem. Bare plutonium sphere with nickel shell")
all_cards1 = [
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

for card in all_cards1:
    input1.addcard(card)
input1.print_to_file()
