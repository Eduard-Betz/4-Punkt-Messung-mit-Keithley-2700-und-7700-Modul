import tkinter as tk
from tkinter import ttk

from global_vars import TKBoardVariabeln, TK_Fehler  # Importiere sowohl TKBoardVariabeln als auch TK_Fehler

def format_number(value):
    if isinstance(value, (int, float)):
        return f"{value:.5f}"
    return value


class SingleBoardLayout:
    def __init__(self, parent_frame, board_nr):
        self.board_nr = board_nr  # z.B. '1', '2', etc.
        self.board_data = TKBoardVariabeln.get_board_data(self.board_nr)
        self.fehler_data = TK_Fehler.get_board_data(self.board_nr)  # Fehlerdaten abrufen
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
        tk.Label(self.board_frame, text="TK ↑ ± Fehler").grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.board_frame, text="TK ↓ ± Fehler").grid(row=1, column=4, padx=5, pady=5)

        # Erstellen Sie Einträge für jeden Widerstand
        self.resistor_entries = {}

        row = 2
        for resistor_nr in sorted(self.board_data.keys(), key=lambda x: int(x)):
            resistor_data = self.board_data[resistor_nr]
            resistor_fehler = self.fehler_data.get(resistor_nr, {}).get('normal', {})
            self.create_resistor_row(row, resistor_nr, resistor_data, resistor_fehler)
            row += 2  # Zwei Zeilen pro Widerstand (normale und gemittelte Daten)

    def create_resistor_row(self, row, resistor_nr, resistor_data, resistor_fehler):
        # Normale Daten aus TKBoardVariabeln
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

        # Fehlerdaten aus TK_Fehler
        delta_alpha_total_steigend = resistor_fehler.get('delta_alpha_total_steigend', "N/A")
        delta_alpha_total_sinkend = resistor_fehler.get('delta_alpha_total_sinkend', "N/A")

        # Formatiere die Steigungswerte mit Fehlern
        steigung_steigend_display = f"{format_number(steigung_steigend)} ± {format_number(delta_alpha_total_steigend)}"
        steigung_sinkend_display = f"{format_number(steigung_sinkend)} ± {format_number(delta_alpha_total_sinkend)}"

        # Gemittelte Daten aus TKBoardVariabeln
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

        # Fehlerdaten für gemittelte Daten aus TK_Fehler
        resistor_fehler_avg = self.fehler_data.get(resistor_nr, {}).get('avg', {})
        delta_alpha_total_avg_steigend = resistor_fehler_avg.get('delta_alpha_total_steigend', "N/A")
        delta_alpha_total_avg_sinkend = resistor_fehler_avg.get('delta_alpha_total_sinkend', "N/A")

        # Formatiere die gemittelten Steigungswerte mit Fehlern
        steigung_avg_steigend_display = f"{format_number(steigung_avg_steigend)} ± {format_number(delta_alpha_total_avg_steigend)}"
        steigung_avg_sinkend_display = f"{format_number(steigung_avg_sinkend)} ± {format_number(delta_alpha_total_avg_sinkend)}"

        # Labels und Entries für normale Daten
        tk.Label(self.board_frame, text=f"R{resistor_nr}").grid(row=row, column=0, padx=5, pady=5)
        tk.Entry(self.board_frame, width=10, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=str(temp_min))).grid(row=row, column=1)
        tk.Entry(self.board_frame, width=10, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=str(temp_max))).grid(row=row, column=2)
        tk.Entry(self.board_frame, width=20, state="readonly", justify="center",  # Breitere Spalte für ± Zeichen
                 textvariable=tk.StringVar(value=steigung_steigend_display)).grid(row=row, column=3)
        tk.Entry(self.board_frame, width=20, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=steigung_sinkend_display)).grid(row=row, column=4)

        # Labels und Entries für gemittelte Daten
        tk.Label(self.board_frame, text=f"Gemit. R{resistor_nr}").grid(row=row+1, column=0, padx=5, pady=5)
        tk.Entry(self.board_frame, width=10, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=str(avg_temp_min))).grid(row=row+1, column=1)
        tk.Entry(self.board_frame, width=10, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=str(avg_temp_max))).grid(row=row+1, column=2)
        tk.Entry(self.board_frame, width=20, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=steigung_avg_steigend_display)).grid(row=row+1, column=3)
        tk.Entry(self.board_frame, width=20, state="readonly", justify="center",
                 textvariable=tk.StringVar(value=steigung_avg_sinkend_display)).grid(row=row+1, column=4)

    def update_data(self):
        # Aktualisiere die Board-Daten aus TKBoardVariabeln und TK_Fehler
        self.board_data = TKBoardVariabeln.get_board_data(self.board_nr)
        self.fehler_data = TK_Fehler.get_board_data(self.board_nr)
        if self.board_data is None:
            print(f"Keine Daten für Board {self.board_nr} gefunden.")
            return

        # Entferne vorhandene Widgets
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        # Re-erstelle die Frame-Struktur und Labels
        self.board_check = tk.Checkbutton(self.board_frame, text=f"Board {self.board_nr}")
        self.board_check.grid(row=0, column=0, columnspan=5, pady=5, sticky='w')

        # Labels für die Spaltenüberschriften
        tk.Label(self.board_frame, text="Resistor").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.board_frame, text="Temp. min").grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.board_frame, text="Temp. max").grid(row=1, column=2, padx=5, pady=5)
        tk.Label(self.board_frame, text="TK ↑ ± Fehler").grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.board_frame, text="TK ↓ ± Fehler").grid(row=1, column=4, padx=5, pady=5)

        # Re-erstelle die Einträge für jeden Widerstand
        row = 2
        for resistor_nr in sorted(self.board_data.keys(), key=lambda x: int(x)):
            resistor_data = self.board_data[resistor_nr]
            resistor_fehler = self.fehler_data.get(resistor_nr, {}).get('normal', {})
            self.create_resistor_row(row, resistor_nr, resistor_data, resistor_fehler)
            row += 2  # Zwei Zeilen pro Widerstand (normale und gemittelte Daten)


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
