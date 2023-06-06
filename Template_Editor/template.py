import re
all_cells = []
all_surfaces = []
all_options = []


def read_template(in_filename):
    f_read = open(in_filename, 'r')
    curr_list = all_cells
    for line in f_read.readlines():
        if re.search(r'\bBegin Surfaces\b', line):
            curr_list = all_surfaces
        elif re.search(r'\bBegin Options\b', line):
            curr_list = all_options

        curr_list.append(line)
    f_read.close()


def print_file(out_filename):
    out_filename = '../mcnp_templates/test.i'
    f_write = open(out_filename, 'w')

    print(all_cells)
    for line in all_cells:
        print(line.strip('\n'), file=f_write)
    for line in all_surfaces:
        print(line.strip('\n'), file=f_write)
    for line in all_options:
        print(line.strip('\n'), file=f_write)
    f_write.close()
    return out_filename
