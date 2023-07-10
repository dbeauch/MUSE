import re

param_cards = [
                re.compile(r'tmp=-?\.?\d+(\.\d+)?[eE]?-?\d*'),
                re.compile(r'imp:n,p=\d+'),
                re.compile(r'\*?trcl=[^a-zA-z]+'),
                re.compile(r'fill=(((-?\d+:-?\d+[ \t]+){3}([ \t]*\d+r?)+))'),
                re.compile(r'lat=\d+'),
                re.compile(r'u=\d+'),
                re.compile(r'vol=-?\.?\d+(\.\d+)?[eE]?-?\d*'),
            ]

origin_param = "tmp=2.747-8 imp:n,p=1 *trcl=(-8.25 5.175 0) u=5 lat=7 f1 f2 f3"
changes = "*trcl=( 0.00 5.175 0)"
line_indent = "     "


# parts = origin_param.split()
# printed_changes = f'\n {line_indent}'.join([' '.join(parts[i:i + 5]) for i in range(0, len(parts), 5)])
# print(printed_changes)


param = []
for regex in param_cards:
    in_changes = regex.search(changes)
    in_origin = regex.search(origin_param)
    if in_changes is not None:
        param.append(in_changes.group())
    elif in_origin is not None:
        param.append(in_origin.group())
cell_param = " ".join(param)
print("1:", cell_param)


final_changes = []
for regex in param_cards:
    combined_match = regex.search(cell_param)
    if combined_match is not None:
        origin_match = regex.search(origin_param)
        if origin_match.group() != combined_match.group():
            final_changes.append(combined_match.group())
changes = " ".join(final_changes)
print(" ".join(final_changes))


# param_origin = []
# param_changes = cell_param
# for regex in param_cards:
#     match = regex.search(param_changes)
#     if match is not None:
#         param_origin.append(match.group())
#         param_changes = param_changes.replace(match.group(), "", 1)  # remove the first occurrence
# # send the parts to origin_cell.param and cell.changes
# changes = " ".join(param_origin)
# origin_param = " ".join(param_changes.split())  # remove leading/trailing/extra white spaces


list = [1, 2, "3"]
print([o for o in list if type(o) is int])
