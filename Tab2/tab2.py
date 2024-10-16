# Tabs/tab2.py
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename

from global_vars import BoardConfig, gefundenen_geraete, Geraet

from Tab2.TabBoards import create_board_tab, update_dropdowns, PreBoardConfig
from Tab2.ConfigTranslator import translate_boardconfig_to_preboard, print_preboard_config
from Tab2.CheckBoardConfig import show_check_result
from Tab2.BoardConfigSaveNLoad import save_config, load_config
from Tab2.ReconnectBoard import reconnect_devices  # Importieren der Reconnect-Funktion

# Definieren des Debug-Flags und der debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def create_tab2(notebook):
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Tab 2")

    button_positions = [
        ("Speichern", 0.0, lambda: save_file()),
        ("Reconekt", 0.1, lambda: reconnect_devices(tab2)),  # Hinzufügen der Reconnect-Funktion
        ("Überprüfen", 0.2, lambda: on_check_button_click(True)),
        ("Laden", 0.8, lambda: load_file(tab2)),
        ("Weiter", 0.9, lambda: handle_next_button_click(notebook))
    ]
    buttons = create_buttons(tab2, button_positions)
    
    notebook.bind("<<NotebookTabChanged>>", lambda event: on_tab_selected(event, notebook, tab2))
    
    gefundenen_geraete.add_callback(lambda: create_board_tab(tab2))
    Geraet.add_callback(update_dropdowns)
    
    return buttons

def create_buttons(tab, button_positions):
    buttons = []
    for text, rel_y, command in button_positions:
        button = tk.Button(tab, text=text, command=command)
        button.place(relx=1, rely=rel_y, anchor='ne', relwidth=0.2, relheight=0.1)
        buttons.append(button)
    return buttons

def on_tab_selected(event, notebook, tab2):
    if notebook.index(notebook.select()) == notebook.tabs().index(str(tab2)):
        num_boards = int(gefundenen_geraete.get_variable('boards'))
        resistors_per_board = int(gefundenen_geraete.get_variable('widerstaende'))

        if num_boards >= 1 and resistors_per_board >= 1:
            if not hasattr(tab2, 'initialized') or not tab2.initialized:
                create_board_tab(tab2)
                tab2.initialized = True

def on_check_button_click(show_all_ok_message):
    all_ok = show_check_result(show_all_ok_message)
    if all_ok:
        debug_print("Alle Widerstände sind korrekt konfiguriert")
    else:
        debug_print("Es gibt Konfigurationsfehler")

def save_file():
    file_path = asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        save_config(file_path)
        debug_print(f"Konfiguration gespeichert unter: {file_path}")

def load_file(tab2):
    global PreBoardConfig
    file_path = askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        load_config(file_path)
        # Aktualisiere die Benutzeroberfläche nach dem Laden der Konfiguration
        board_config = BoardConfig.get_board_config()
        PreBoardConfig = translate_boardconfig_to_preboard(board_config)
        create_board_tab(tab2)
        update_dropdowns()
        debug_print("Benutzeroberfläche nach dem Laden aktualisiert.")
        debug_print("Geladene PreBoardConfig:")
        print_preboard_config(PreBoardConfig)

def handle_next_button_click(notebook):
    all_ok = show_check_result(False)  # Überprüft die Konfiguration, ohne ein Fenster anzuzeigen
    if all_ok:
        # Speichern der BoardConfig in einer festen Datei
        file_name = "BoardConfig.json"
        save_config(file_name)
        debug_print(f"Konfiguration gespeichert unter: {file_name}")
        # Wechseln zu tab3
        notebook.select(2)  # Angenommen, tab3 ist das dritte Tab, der Index kann angepasst werden
    else:
        debug_print("Es gibt Konfigurationsfehler, bitte überprüfen.")

def print_configs():
    from Tab2.TabBoards import print_board_config
    debug_print("Aktuelle Board-Konfiguration:")
    print_board_config()
