# tab1.py
import tkinter as tk
from tkinter import ttk

from global_vars import gefundenen_geraete

from resize_handler import on_resize

from Tab1.TabGeraete import create_tab_geraete
from Tab1.KontroleTabConfig import print_geräte_check


DEBUG = False

def debug_Tab1_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# Globale Variablen deklarieren
baudrate_var = None
anzahl_var = None
boards_var = None
widerstaende_var = None

def validate_integer_input(value_if_allowed):
    if value_if_allowed.isdigit() and int(value_if_allowed) >= 1:
        return True
    elif value_if_allowed == "":
        return True
    else:
        return False

def create_tab1(notebook, finder_callback):
    global baudrate_var, anzahl_var, boards_var, widerstaende_var

    # Initialisierung der Variablen innerhalb der Funktion
    baudrate_var = tk.StringVar(value="9600")
    anzahl_var = tk.StringVar()
    boards_var = tk.StringVar()
    widerstaende_var = tk.StringVar()

    # Callbacks hinzufügen
    baudrate_var.trace_add("write", lambda *args: update_global_var('baudrate', baudrate_var.get()))
    anzahl_var.trace_add("write", lambda *args: update_global_var('anzahl', anzahl_var.get()))
    boards_var.trace_add("write", lambda *args: update_global_var('boards', boards_var.get()))
    widerstaende_var.trace_add("write", lambda *args: update_global_var('widerstaende', widerstaende_var.get()))

    debug_Tab1_print("Initializing Tab 1:")
    debug_Tab1_print(f"boards_var initialized: {boards_var}")
    debug_Tab1_print(f"widerstaende_var initialized: {widerstaende_var}")

    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Tab 1")

    main_settings_frame = ttk.LabelFrame(tab1, text="Einstellungen", labelanchor="n")
    main_settings_frame.place(relx=0.05, rely=0.05, anchor='nw', relwidth=0.15)

    # Validierung für Eingabefelder erstellen
    vcmd = (tab1.register(validate_integer_input), '%P')

    # Geräteeinstellungen
    settings_frame1 = ttk.LabelFrame(main_settings_frame, text="Geräteeinstellungen", labelanchor="n")
    settings_frame1.pack(padx=10, pady=10, fill="x")

    # Baudrate-Auswahl
    baudrate_frame = ttk.LabelFrame(settings_frame1, text="Baudrate Auswahl", labelanchor="n")
    baudrate_frame.pack(padx=10, pady=10, fill="x")

    baudrate_menu = tk.OptionMenu(baudrate_frame, baudrate_var, *["300", "1200", "2400", "4800", "9600", "19200"])
    baudrate_menu.pack(padx=10, pady=5, fill="x")

    # Anzahl der Geräte
    anzahl_frame = ttk.LabelFrame(settings_frame1, text="Anzahl der Geräte", labelanchor="n")
    anzahl_frame.pack(padx=10, pady=10, fill="x")

    anzahl_entry = ttk.Entry(anzahl_frame, textvariable=anzahl_var, width=5, justify='center', validate='key', validatecommand=vcmd)
    anzahl_entry.pack(padx=10, pady=5)

    # Boardeinstellungen
    settings_frame2 = ttk.LabelFrame(main_settings_frame, text="Boardeinstellungen", labelanchor="n")
    settings_frame2.pack(padx=10, pady=10, fill="x")

    # Anzahl der Boards
    boards_frame = ttk.LabelFrame(settings_frame2, text="Anzahl der Boards", labelanchor="n")
    boards_frame.pack(padx=10, pady=10, fill="x")

    boards_entry = ttk.Entry(boards_frame, textvariable=boards_var, width=5, justify='center', validate='key', validatecommand=vcmd)
    boards_entry.pack(padx=10, pady=5)

    # Widerstände pro Board
    widerstaende_frame = ttk.LabelFrame(settings_frame2, text="Widerstände pro Board", labelanchor="n")
    widerstaende_frame.pack(padx=10, pady=10, fill="x")

    widerstaende_entry = ttk.Entry(widerstaende_frame, textvariable=widerstaende_var, width=5, justify='center', validate='key', validatecommand=vcmd)
    widerstaende_entry.pack(padx=10, pady=5)

    # Beobachter hinzufügen
    boards_var.trace_add("write", lambda *args: variable_changed('boards_var', *args))
    widerstaende_var.trace_add("write", lambda *args: variable_changed('widerstaende_var', *args))

    # Füge die Buttons am rechten Rand hinzu
    button_positions = [("Suchen", 0, finder_callback), ("Prüfen", 0.1, lambda: print_geräte_check(baudrate_var, anzahl_var, boards_var, widerstaende_var, True)), ("Weiter", 0.9, lambda: handle_knopf3_click(notebook))]
    buttons = create_buttons(tab1, button_positions)

    # Knopf 2 deaktivieren, wenn anzahl_var leer oder null ist
    def update_button_state(*args):
        if not anzahl_var.get().isdigit() or int(anzahl_var.get()) == 0:
            buttons[1].config(state='disabled')
        else:
            buttons[1].config(state='normal')

    anzahl_var.trace_add("write", update_button_state)
    update_button_state()  # Initialer Aufruf, um den Button entsprechend zu setzen

    # Erstelle den neuen Tab innerhalb von Tab1
    create_tab_geraete(tab1, anzahl_var)

    # Binde das <Configure> Event, um die Schriftgröße der Buttons und anderer Elemente anzupassen
    elements_to_resize = buttons + [baudrate_menu, anzahl_entry, boards_entry, widerstaende_entry]
    tab1.bind("<Configure>", lambda event: on_resize(event, tab1, elements_to_resize))

def create_buttons(tab, button_positions):
    buttons = []
    for text, rel_y, command in button_positions:
        button = tk.Button(tab, text=text, command=command)
        button.place(relx=1, rely=rel_y, anchor='ne', relwidth=0.2, relheight=0.1)
        buttons.append(button)
    return buttons

def variable_changed(var_name, *args):
    value = globals()[var_name].get()
    if value == "":
        debug_Tab1_print(f"{var_name}: ''")  # Leerzeichen bei leerer Eingabe
    elif not value.isdigit() or int(value) < 1:
        globals()[var_name].set("0")
    else:
        debug_Tab1_print(f"{var_name}: {value}")

def print_gefundenen_geraete():
    global gefundenen_geraete
    if not gefundenen_geraete.geraete or (len(gefundenen_geraete.geraete) == 1 and gefundenen_geraete.geraete[0] == ["NaN", "NaN", "NaN", "NaN"]):
        debug_Tab1_print("Keine Geräte gefunden.")
    else:
        for port, idn, mod1, mod2 in gefundenen_geraete.geraete:
            debug_Tab1_print(f"Port: {port}, IDN: {idn}, Modul in Port 1: {mod1}, Modul in Port 2: {mod2}")

def handle_knopf3_click(notebook):
    if not print_geräte_check(baudrate_var, anzahl_var, boards_var, widerstaende_var, False):
        # Wechsel zu Tab2, wenn keine Fehler gefunden wurden und kein Fenster geöffnet wurde
        notebook.select(1)

def update_global_var(var_name, value):
    global gefundenen_geraete
    gefundenen_geraete.update_variable(var_name, value)
