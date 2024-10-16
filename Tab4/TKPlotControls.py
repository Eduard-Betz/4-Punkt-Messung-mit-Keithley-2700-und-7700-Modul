#TKPlotCronrols.py


import tkinter as tk
from tkinter import ttk

from global_vars import TKBoardVariabeln


class SingleBoardLayout:
    def __init__(self, parent_frame, board_nr):
        self.board_nr = board_nr  # z.B. '1', '2', etc.
        self.board_data = TKBoardVariabeln.get_board_data(self.board_nr)
        if self.board_data is None:
            print(f"Keine Daten für Board {self.board_nr} gefunden.")
            return

        # Frame für das einzelne Board
        self.board_frame = tk.Frame(parent_frame, bd=2, relief="groove")
        self.board_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Checkbutton für das Board
        self.board_check = tk.Checkbutton(self.board_frame, text=f"Board {self.board_nr}")
        self.board_check.grid(row=0, column=0, columnspan=5, pady=5, sticky='w')

        # Labels für die Spaltenüberschriften
        tk.Label(self.board_frame, text="Resistor").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.board_frame, text="Temp. min").grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.board_frame, text="Temp. max").grid(row=1, column=2, padx=5, pady=5)
        tk.Label(self.board_frame, text="TK ↑").grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.board_frame, text="TK ↓").grid(row=1, column=4, padx=5, pady=5)

        # Erstellen Sie Einträge für jeden Widerstand
        self.resistor_entries = {}

        row = 2
        for resistor_nr in sorted(self.board_data.keys(), key=lambda x: int(x)):
            resistor_data = self.board_data[resistor_nr]
            self.create_resistor_row(row, resistor_nr, resistor_data)
            row += 2  # Zwei Zeilen pro Widerstand (normale und gemittelte Daten)

    def create_resistor_row(self, row, resistor_nr, resistor_data):
        # Normale Daten
        normal_data = resistor_data.get('normal', {})
        temp_min_max = normal_data.get('temp_bereich_steigend', (None, None))
        temp_min_s_max_s = normal_data.get('temp_bereich_sinkend', (None, None))

        temp_min_list = [temp_min_max[0], temp_min_s_max_s[0]]
        temp_max_list = [temp_min_max[1], temp_min_s_max_s[1]]

        # Filtern von None-Werten
        temp_min_list = [t for t in temp_min_list if t is not None]
        temp_max_list = [t for t in temp_max_list if t is not None]

        temp_min = min(temp_min_list) if temp_min_list else "N/A"
        temp_max = max(temp_max_list) if temp_max_list else "N/A"

        steigung_steigend = normal_data.get('steigung_steigend', "N/A")
        steigung_sinkend = normal_data.get('steigung_sinkend', "N/A")

        # Gemittelte Daten
        avg_data = resistor_data.get('avg', {})
        avg_temp_min_max = avg_data.get('temp_bereich_steigend', (None, None))
        avg_temp_min_s_max_s = avg_data.get('temp_bereich_sinkend', (None, None))

        avg_temp_min_list = [avg_temp_min_max[0], avg_temp_min_s_max_s[0]]
        avg_temp_max_list = [avg_temp_min_max[1], avg_temp_min_s_max_s[1]]

        # Filtern von None-Werten
        avg_temp_min_list = [t for t in avg_temp_min_list if t is not None]
        avg_temp_max_list = [t for t in avg_temp_max_list if t is not None]

        avg_temp_min = min(avg_temp_min_list) if avg_temp_min_list else "N/A"
        avg_temp_max = max(avg_temp_max_list) if avg_temp_max_list else "N/A"

        steigung_avg_steigend = avg_data.get('steigung_steigend', "N/A")
        steigung_avg_sinkend = avg_data.get('steigung_sinkend', "N/A")

        # Labels und Entries für normale Daten
        tk.Label(self.board_frame, text=f"R{resistor_nr}").grid(row=row, column=0, padx=5, pady=5)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(temp_min))).grid(row=row, column=1)
        tk.Entry(self.board_frame, width=10, state="readonly",
             textvariable=tk.StringVar(value=str(temp_max))).grid(row=row, column=2)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(steigung_steigend))).grid(row=row, column=3)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(steigung_sinkend))).grid(row=row, column=4)

        # Labels und Entries für gemittelte Daten
        tk.Label(self.board_frame, text=f"Gemit. R{resistor_nr}").grid(row=row+1, column=0, padx=5, pady=5)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(avg_temp_min))).grid(row=row+1, column=1)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(avg_temp_max))).grid(row=row+1, column=2)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(steigung_avg_steigend))).grid(row=row+1, column=3)
        tk.Entry(self.board_frame, width=10, state="readonly",
                 textvariable=tk.StringVar(value=str(steigung_avg_sinkend))).grid(row=row+1, column=4)


    def update_data(self):
        # Aktualisiere die Board-Daten aus TKBoardVariabeln
        self.board_data = TKBoardVariabeln.get_board_data(self.board_nr)
        if self.board_data is None:
            print(f"Keine Daten für Board {self.board_nr} gefunden.")
            return

        # Aktualisiere die Daten für jeden Widerstand
        row = 2
        for resistor_nr in sorted(self.board_data.keys(), key=lambda x: int(x)):
            resistor_data = self.board_data[resistor_nr]
            # Aktualisieren Sie die Einträge hier, falls erforderlich
            row += 2

def create_multiple_boards(parent_notebook):
    board_data = TKBoardVariabeln.board_variablen
    sorted_board_list = sorted(board_data.keys(), key=lambda x: int(x))
    
    boards_per_tab = 5
    num_boards = len(sorted_board_list)
    num_tabs = (num_boards + boards_per_tab - 1) // boards_per_tab  # Rundet auf

    board_layouts = []
    for tab_index in range(num_tabs):
        start_index = tab_index * boards_per_tab
        end_index = min(start_index + boards_per_tab, num_boards)
        tab_boards = sorted_board_list[start_index:end_index]

        # Erstellen eines neuen Frames für den Tab
        tab_frame = ttk.Frame(parent_notebook)

        # Hinzufügen des Tabs zum Notebook mit passendem Namen
        tab_name = f"Board {start_index+1}-{end_index}"
        parent_notebook.add(tab_frame, text=tab_name)

        # Erstellen der Boards innerhalb des Tab-Frames
        for board_nr in tab_boards:
            board_frame = tk.Frame(tab_frame)
            board_frame.pack(fill="x", padx=5, pady=5)

            board_layout = SingleBoardLayout(board_frame, board_nr)
            board_layouts.append(board_layout)
    return board_layouts


def update_TKboards(board_layouts):
    for board_layout in board_layouts:
        board_layout.update_data()
