from mendeleev import element
from mendeleev.fetch import fetch_table
# element_number = "11"
# element_name = element(element_number).symbol
#
# print(f"'{element_number}': '{element_name}',")

zaid = "100000."

if len(zaid) < 4 or 'c' in zaid or '.' in zaid:
    print('Unrecognized ZAID')
