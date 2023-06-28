from mcnp_cards import *

cell1 = RegularCell("1 1 1 1")
cell2 = VoidCell("2 0  1")
cell3 = LikeCell("3 like 2 but mat=3")

print(type(cell1))
print(type(cell1) is RegularCell)
