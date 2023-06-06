import re
cell_lines = []
surface_lines = []
data_lines = []

all_cells = {}
all_surfaces = {}
all_materials = {}
all_options = []


def read_template(in_filename):
    f_read = open(in_filename, 'r')
    curr_list = cell_lines
    for line in f_read.readlines():
        if re.search(r'\bBegin Surfaces\b', line):
            curr_list = surface_lines
        elif re.search(r'\bBegin Options\b', line):
            curr_list = data_lines

        curr_list.append(line)
    f_read.close()


def print_file(out_filename):
    #out_filename = '../mcnp_templates/test.i'
    f_write = open(out_filename, 'w')

    """for line in all_cells:
        print(line.strip('\n'), file=f_write)
    for line in all_surfaces:
        print(line.strip('\n'), file=f_write)
    for line in all_options:
        print(line.strip('\n'), file=f_write)"""
    f_write.close()
    return out_filename
