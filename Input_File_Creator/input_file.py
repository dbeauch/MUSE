from Input_File_Creator.mcnp_cards import *
class InputFile:
    def __init__(self, file_name, title_card="No Title"):
        self.file_name = file_name
        self.title_card = title_card
        self.all_cell_cards = []
        self.all_surface_cards = []
        self.all_data_cards = []

    def __str__(self):
        return f"{self.file_name} contains {self.title_card}"

    def addcard(self, card):
        if isinstance(card, CellCard):
            self.all_cell_cards.append(card)
        if isinstance(card, SurfaceCard):
            self.all_surface_cards.append(card)
        if isinstance(card, DataCard):
            self.all_data_cards.append(card)
        if isinstance(card, SquareLattice):
            for cell in card.cells:
                self.all_cell_cards.append(cell)
            for surface in card.surfaces:
                self.all_surface_cards.append(surface)

    def print_to_file(self, file=""):
        if file == "":
            file = self.file_name

        blank_line_delimiter = ""
        f = open(file, "w")  # overwrite existing text
        f = open(file, "a")  # appending from here on

        # TITLE CARD
        print(self.title_card, file=f)

        # CELL CARDS
        print("C\tCell Cards", file=f)
        for cell in self.all_cell_cards:
            print(cell, file=f)
        print(blank_line_delimiter, file=f)

        # SURFACE CARDS
        print("C\tSurface Cards", file=f)
        for surface in self.all_surface_cards:
            print(surface, file=f)
        print(blank_line_delimiter, file=f)

        # DATA CARDS
        print("C\tData Cards", file=f)
        for data in self.all_data_cards:
            print(data, file=f)
        # print(blank_line_delimiter, file=f)  # optional eof

        f.close()
