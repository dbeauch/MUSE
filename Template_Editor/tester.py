import re
from template_handler import *
from mcnp_cards import *
import sys

"""
create a dash app to edit MCNP input files. I have already created all the pre and post processing code that handles making the changes to the file. I want this dash app to be the front end portion of the app that lets the user enter changes to different cards, apply those changes with a button, and a button to print the file. Your methods called by the buttons need only exist and i will fill in the code to activate input file changes. The dash app you should create will just be a testing shell for me to build off of 

this is good. I now want you to make these changes. Remove the simple enter card changes input text box. Make a drop down selector that displays all known cells by their number which I will implement and the user should be able to search for the cell number they want to change. Next to that selector make a similar one that will be the material to apply to the cell as a change, it should also display a searchable list of known materials that i will implement. Place the apply changes button next to this and add a divider between the changes section and the print file section. The print file section should contain the print file button and an output that tells the user the file was printed to the file supplied via an input text box. I will implement whatever you cannot

great. now edit the code to make these changes: messages displayed to the user are displayed in a console at the bottom of the screen, the console should have a gray background with white text. The background of the whole app should be a darker gray than the console. Style the title of the webpage with a green banner on the top with the app name. Create an app name for this site based on the keywords Py, Python, MCNP, Monte, Carlo, Edit or add whatever else seems suit

great. now make the following changes: extend the page down to the bottom of the screen with the same dark gray background coloring. Change the console messages so that it keeps at least the last 5 things printed to the screen in view. The console shoudl be scrollable so that the user can view previous console messages

make the following changes: extend the background dark gray color so that there is no white space on the edges. The sit should fit on one page with no option to scroll down. The console should be justified on the bottom of the page. Change the banner on the top so that the app title is Py2MCNP Editor and make the banner color a geometric patterned light and dark blue. Have the style of the page mimic that of the webpage for NIST found at: https://www.nist.gov/ncnr if possible

add a black frame below the title banner and around the console. add a small header left justified to the cell editor section that denotes it as the section for cell changes and the same for the printing section

the layout of the page is good. black frame around console and below banner is good. cell changes and printing section headers are good, but revert the app color and top banner style to the previous one while maintaining the things that are good.

good. make the following changes: increase the size of the top banner and make the app title Py2MCNP Editor larger. Add a small separator between the cell changes and printing sections. Make the text displayed in the console slightly gray

add a scrolling function to the console log so that the user can see the previous messages 
"""

line = "m4644 92232 -1.80000E-09 92234 -2.34000E-03 "

zaid_fracs = []
number_end = re.search(r'^m\d+', line).span()[1] + 1
number = line[1: number_end].strip()
zaid_list = re.split(r'[ \t]+', line[number_end:].strip())
for i in range (int(len(zaid_list) / 2)):
    zaid_fracs.append((zaid_list[2*i], zaid_list[2*i + 1]))


# last_pair_end = number_end
# indexer = number_end
# curr_pair_end = re.search(r'\d+[ \t]+-?\d+(\.\d+)?[eE]?-?\d*[ \t]+', line[indexer:]).span()[1] + 1
# while curr_pair_end is not None:
#     indexer += last_pair_end
#     zaid_fracs.append(line[indexer: curr_pair_end].strip())
#     last_pair_end = curr_pair_end
#     curr_pair_end = re.search(r'\d+[ \t]+-?\d+(\.\d+)?[eE]?-?\d*[ \t]+', line[indexer + last_pair_end:]).span()[1] + 1
sys.setrecursionlimit(8000)
read_template('../mcnp_templates/burn_Box9_v02_SU_cycle8.i')
