import re
from mcnp_cards import *

all_cell_lines = []
all_material_lines = []

all_cells = {}
cell_comments = {}
all_surfaces = {}
all_materials = {}
material_comments = {}


def clean(line_array, comment_array):
    i = 0
    while i < len(line_array):
        dollar_index = re.search(r'\$.*$', line_array[i])
        if dollar_index is not None:
            if re.search(r'^m?\d{1,6}', line_array[i]) is not None:
                new_comment = line_array[i][dollar_index.span()[0] + 1:].strip()
                number_end = re.search(r'^m?\d{1,6}', line_array[i]).span()[1] + 1
                number = line_array[i][0: number_end].strip()
                comment_array[number] = new_comment
                line_array[i] = line_array[i][: dollar_index.span()[0]]
        if re.search(r'^[cC].*$', line_array[i]) is not None:
            line_array.pop(i)
            i -= 1
        i += 1
    return

    # i = 0
    # while i < len(line_array):
    #     if re.search(r'^[cC].*$', line_array[i]) is not None:  # Catch all comments
    #         if re.search(r'^[cC][ \t]+\S.*$', line_array[i]) is not None:  # Catch only comments with content
    #             if i < len(line_array) - 1 and re.search(r'^m?\d{1,6}', line_array[i + 1]) is not None:
    #                 number_end = re.search(r'^m?\d{1,6}', line_array[i + 1]).span()[1] + 1
    #                 number = line_array[i + 1][0: number_end].strip()
    #                 comment_array[number] = line_array[i]
    #         line_array.pop(i)
    #         i -= 1
    #     i += 1
    return


lits = [
    'c --Begin Cells--                          ',
    '1      0          8:9:-10  tmp=2.747-8 imp:n,p=0                               $ outside of water pool',
    '2      4 -0.99180 -7 -9 10 (11:21:-31)                                         $ light water pool   ',
    '                  (-1001:1006:-2001:2006:-31:898)  ',
    'c cold sources:',
    '                  (-4030:4031:4032:-4033:4034)',
    '                  ( 4130:4131:4132:-4133:4134)',
    '                  (-5030:5031:5032:-4033:4034)',
    '                  ( 5330:5331:5332:-4133:4134)',
    'c beam tubes:',
    '             (-9110:9111:-9104:9107:9109) (9100:9109) (9103:9109)',
    '             (-9210:9211:-9204:9207:9209) (9200:9209) (9203:9209)',
    '             (-9310:9311:-9304:9307:9309) (9300:9309) (9303:9309)',
    '             (-9410:9411:-9404:9407:9409) (9400:9409) (9403:9409)',
    '                  tmp=2.747-8 imp:n,p=1                             ',
    'c ',
    '3      5 -6.55    -11 -21 31 (1:2:-3)                                          $ heavy water outer tank container                  ',
    '                  (1006:-1001:2006:-2001) imp=1',
    ]
material = [
    'm2395 $ commy',
    '           92234  -2.296177e-03      $ U-234',
    '           92234  -2.296177e-03      $ U-234',
    '           92234  -2.296177e-03      $ U-234',
    '           92234  -2.296177e-03      $ U-234',
    '           92234  -2.296177e-03      $ U-234',
    '           92237  -4.831449e-06      $',
           # 94238  -3.258481e-07      $
           # 94242  -1.972536e-08      $'
]

clean(lits, cell_comments)
print(lits)
print(cell_comments)
