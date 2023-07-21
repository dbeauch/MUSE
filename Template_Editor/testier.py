param = "tmp=2.747-8 imp:n,p=1 u=100 lat=1"
fill_range = "fill="
fill = "-11:11 0:0 0:0  100 200 20r 100 "

param1 = "tmp=2.747-8 imp:n,p=1 u=900 "
fill_range1 = "fill="
fill1 = "100"

parts = param.split()
for w in fill_range.strip().split():
    parts.append(w)
for w in fill:
    parts.append(w)

parts1 = param1.split()
for w in fill_range1.strip().split():
    parts1.append(w)
for w in fill1:
    parts1.append(w)

# for w in fill_range.strip().split():
#     parts.append(w)
# for w in fill:
#     parts.append(w)
# # Print changes with newlines every 5 spaces
printed_changes2 = f'\n {"             "}'.join([' '.join(parts[i:i + 5]) for i in range(0, len(parts), 5)])

printed_param = f'\n{"             "}'.join([' '.join(parts[i:i + 5]) + "             " for i in range(0, len(parts), 5)])
printed_param1 = f'\n{"             "}'.join([' '.join(parts1[i:i + 5]) + "             " for i in range(0, len(parts1), 5)])

# print(parts)
# print(parts1)
#
# print(printed_param)
# print(printed_param1)
# print(printed_changes2)
print("".join(['1']))
print(["1"])

