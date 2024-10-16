# TabGeraete.py
from tkinter import ttk

from global_vars import gefundenen_geraete, Geraet

from Tab1.SingleGeraetelayer import SingleGeraetelayer



# Definiere das Debug-Flag und die debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def create_tab_geraete(parent, anzahl_var):
    tab_geraete = ttk.Frame(parent, borderwidth=2, relief="sunken")
    tab_geraete.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.9)

    # Initialisiere den Geräte-Manager
    geraete_manager = Geraet

    # Anzahl der Geräte überwachen und aktualisieren
    anzahl_var.trace_add("write", lambda *args: update_geraete(tab_geraete, anzahl_var, geraete_manager))
    gefundenen_geraete.add_callback(lambda: update_geraete(tab_geraete, anzahl_var, geraete_manager))

    update_geraete(tab_geraete, anzahl_var, geraete_manager)

def update_geraete(tab_geraete, anzahl_var, geraete_manager):
    for widget in tab_geraete.winfo_children():
        widget.destroy()

    anzahl_str = anzahl_var.get()
    anzahl = int(anzahl_str) if anzahl_str.isdigit() else 0

    devices = gefundenen_geraete.geraete.copy()

    # Fülle die Liste mit "NaN"-Geräten auf, falls anzahl_var größer ist als die Anzahl der gefundenen Geräte
    if anzahl > len(devices):
        devices.extend([["NaN", "NaN", "NaN", "NaN"]] * (anzahl - len(devices)))

    # Beschränke die Anzahl der Geräte in geraete_manager auf anzahl_var
    geraete_manager.geraete = geraete_manager.geraete[:anzahl]

    current_tab = None
    tab_widget = ttk.Notebook(tab_geraete)
    tab_widget.pack(fill="both", expand=True, padx=10, pady=10)

    for i in range(anzahl):
        if i % 4 == 0:
            current_tab = ttk.Frame(tab_widget, borderwidth=2, relief="sunken")
            tab_name = f"{i + 1}-{min(i + 4, anzahl)}"
            tab_widget.add(current_tab, text=tab_name)

        row, col = divmod(i % 4, 2)
        device_layer = SingleGeraetelayer(current_tab, devices, devices[i][0], i + 1, devices[i])
        device_layer.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Update the device settings in the manager
        geraete_manager.update_geraet(i + 1, devices[i][0], devices[i][2], devices[i][3])

    # For debugging, print the current device settings
    debug_print("Aktuelle Geräteeinstellungen:")
    for geraet in geraete_manager.geraete:
        debug_print(geraet)
