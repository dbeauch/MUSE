import re
line_indent = f"\t\t\t"
geom = "1002 -1005 2002 -2005 984 -985 834 835 836 837 838 839 (-911:912:-915:916)"

printed_geom = re.sub(r'\)[ \t]+\(', f")\n{line_indent}(", geom)
printed_geom = re.sub(r':[ \t]+\(', f":\n{line_indent}(", printed_geom)
digit_par = re.search(r'\d[ \t]+\(', printed_geom)
if digit_par is not None:
    printed_geom = printed_geom[:digit_par.span()[0]+1] + f"\n{line_indent}" + printed_geom[digit_par.span()[0]+2:]

print(printed_geom)
