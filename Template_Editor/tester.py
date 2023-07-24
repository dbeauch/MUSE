import re

fills = ['200', '2r', '300', '400']  # example input list
expanded_fills = []

for i, fill in enumerate(fills):
    if 'r' in fill:
        repeats = int(re.search(r'\d+', fill).group())  # extract the number before 'r'
        if i > 0 and fills[i-1].isdigit():  # check if preceding element is a number
            expanded_fills.extend([fills[i-1]] * repeats)  # add the preceding element repeated 'repeats' times
    else:
        expanded_fills.append(fill)  # if current element doesn't contain 'r', just add it to the new list

fills = expanded_fills
print(fills)  # output: ['200', '200', '200', '300', '400']
