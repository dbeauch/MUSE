import re
line_indent = f"\t\t\t"
geom = "1002 -1005 2002 -2005 984 -985 834 835 836 837 838 839 (-911:912:-915:916) 5 5 5 5 5 5 6 7 8 "

# printed_changes = ""
# last_break = 0
# space_break = re.search(r'(\S+ ){5}', geom)
# while space_break is not None:
#     printed_changes += geom[last_break: space_break.span()[1] + last_break] + "\n"
#     last_break = space_break.span()[1]
#     new_break = geom[last_break:]
#     space_break = re.search(r'( \S+){5}', geom[last_break:])
# printed_changes += geom[last_break:]
# print(printed_changes)

printed_changes = ""
parts = geom.split()
for i in range(0, len(parts), 5):
    printed_changes += ' '.join(parts[i:i + 5]) + "\n" + line_indent
printed_changes = printed_changes[:re.search(r'\s+$', printed_changes).span()[0]]
print(printed_changes)
print("nextline")