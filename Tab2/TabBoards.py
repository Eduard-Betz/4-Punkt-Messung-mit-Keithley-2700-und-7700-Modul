# Tabs/TabBoards.py
import tkinter as tk
from tkinter import ttk

from global_vars import gefundenen_geraete, Geraet, BoardConfig

from Tab2.SingleBoardLayer import create_board_frame
from Tab2.ConfigTranslator import translate_preboard_to_boardconfig, translate_boardconfig_to_preboard

PreBoardConfig = []  # Definiere PreBoardConfig als globale Variable

# Definieren des Debug-Flags und der debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def create_board_tab(tab2):
    global PreBoardConfig  # Verweise auf die globale Variable PreBoardConfig
    board_tab_container = ttk.Frame(tab2, padding="10")  # Rahmen um das Fenster
    board_tab_container.place(relx=0, rely=0, relwidth=0.8, relheight=1.0)

    notebook = ttk.Notebook(board_tab_container)
    notebook.pack(expand=1, fill="both")

    # Konvertiere Geraet.geraete in das erwartete Format
    devices = []
    for device in Geraet.geraete:
        device_info = {
            'device_number': device[0],
            'multiplexer1': device[2] != 'NaN',
            'multiplexer2': device[3] != 'NaN'
        }
        devices.append(device_info)

    debug_print(f"Konvertierte Geräte: {devices}")

    # Erstelle die Board Frames abhängig von der Anzahl der Boards und Widerstände
    num_boards = int(gefundenen_geraete.get_variable('boards'))
    resistors_per_board = int(gefundenen_geraete.get_variable('widerstaende'))

    if resistors_per_board < 1:
        debug_print("Fehler: Anzahl der Widerstände pro Board ist kleiner als 1.")
        return None, []

    debug_print(f"Anzahl der Boards: {num_boards}, Widerstände pro Board: {resistors_per_board}")

    PreBoardConfig = translate_boardconfig_to_preboard(BoardConfig.get_board_config())  # Initialisiere PreBoardConfig mit geladenen Daten
    while len(PreBoardConfig) < num_boards:
        PreBoardConfig.append({'frame': None, 'resistors': []})

    board_counter = 0
    tab_counter = 1

    for board_num in range(1, num_boards + 1):
        if board_counter % 10 == 0:
            if board_counter == 0:
                tab_name = ""
            else:
                start_board_num = board_counter + 1
                end_board_num = min(start_board_num + 9, num_boards)
                tab_name = f"{start_board_num}-{end_board_num}"
                notebook.tab(0, text=f"1-{min(10, num_boards)}")  # Setze den Namen des ersten Tabs
            
            # Erstelle einen neuen Tab mit Scrollfunktion
            current_tab = ttk.Frame(notebook)
            notebook.add(current_tab, text=tab_name)

            canvas = tk.Canvas(current_tab)
            scrollbar = ttk.Scrollbar(current_tab, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Bind Mouse Wheel to Canvas
            canvas.bind_all("<MouseWheel>", lambda event, c=canvas: on_mouse_wheel(event, c))

            tab_counter += 1
            row_counter = 0
            col_counter = 1  # Starten Sie in Spalte 1, um Platz für Zentrierung zu lassen

            # Centering the frames
            scrollable_frame.grid_rowconfigure(0, weight=1)
            for i in range(1, 6):
                scrollable_frame.grid_rowconfigure(i, weight=0)
            scrollable_frame.grid_rowconfigure(6, weight=1)

            scrollable_frame.grid_columnconfigure(0, weight=1)
            for i in range(1, 5):
                scrollable_frame.grid_columnconfigure(i, weight=0)
            scrollable_frame.grid_columnconfigure(5, weight=1)  # Mehr Platz zwischen den Spalten

        # Füge die Daten aus PreBoardConfig hinzu, wenn sie existieren
        preboard_resistors = None
        if board_num <= len(PreBoardConfig):
            preboard_resistors = PreBoardConfig[board_num - 1]['resistors']

        board_data = create_board_frame(scrollable_frame, board_num, devices, resistors_per_board, preboard_resistors)
        PreBoardConfig[board_num - 1] = board_data

        board_data['frame'].grid(row=row_counter + 1, column=col_counter + 1, padx=10, pady=10, sticky="nsew")

        board_counter += 1
        row_counter += 1

        if row_counter >= 5:
            row_counter = 0
            col_counter += 2  # Mehr Platz zwischen den Spalten

        debug_print(f"Erstellt Board {board_num} mit {len(board_data['resistors'])} Widerständen")

    # Übersetze und speichere die BoardConfig
    board_config = translate_preboard_to_boardconfig(PreBoardConfig)
    BoardConfig.update_board_config(board_config)

    return board_tab_container, PreBoardConfig

def update_dropdowns():
    global PreBoardConfig
    devices = []
    for device in Geraet.geraete:
        device_info = {
            'device_number': device[0],
            'multiplexer1': device[2] != 'NaN',
            'multiplexer2': device[3] != 'NaN'
        }
        devices.append(device_info)

    for board in PreBoardConfig:
        for resistor in board['resistors']:
            selected_device = resistor['selected_device']
            dropdown = resistor['dropdown']
            device_options = []
            for device in devices:
                device_number = device['device_number']
                if device['multiplexer1']:
                    for ch in range(1, 11):
                        device_options.append(f"{device_number}. 1. Channel {ch:02d} & {ch + 10:02d}")
                if device['multiplexer2']:
                    for ch in range(1, 11):
                        device_options.append(f"{device_number}. 2. Channel {ch:02d} & {ch + 10:02d}")
            dropdown['values'] = device_options
            dropdown.set(selected_device.get())  # Setze den Wert des Dropdown-Menüs

def on_device_change():
    update_dropdowns()
    debug_print("Dropdown-Menüs aktualisiert")

def print_board_config():
    board_config = BoardConfig.get_board_config()
    debug_print("Aktuelle BoardConfig:")
    for config in board_config:
        debug_print(config)
