# KontroleTabConfig.py

import tkinter as tk
from tkinter import ttk

from global_vars import Geraet, gefundenen_geraete  # Importiere die globale Geräteverwaltung

from Tab1.finder import Finder

def geräte_check(baudrate):
    fehlerhafte_geraete = []
    ports = {}
    finder = Finder(baudrate)
    neue_geraete = []

    for geraet in Geraet.geraete:
        geraet_nummer, port, mod1, mod2 = geraet

        if port == "NaN":
            fehlerhafte_geraete.append((geraet, "Port ist NaN"))
        else:
            idn, found_mod1, found_mod2 = finder.find_device(port)
            if idn is None:
                fehlerhafte_geraete.append((geraet, "Kein Gerät gefunden"))
            else:
                # Aktualisiere Geraet in der globalen Liste
                Geraet.update_geraet(geraet_nummer, port, found_mod1, found_mod2)
                neue_geraete.append((port, idn, found_mod1, found_mod2))
            
            if port in ports:
                ports[port].append(geraet)
            else:
                ports[port] = [geraet]

    for port, geraete in ports.items():
        if len(geraete) > 1:
            for geraet in geraete:
                fehlerhafte_geraete.append((geraet, f"Doppelter Port: {port}"))

    # Aktualisiere die gefundenen Geräte
    gefundenen_geraete.update_geraete(neue_geraete)

    # Fehlerprüfung, nachdem die Geräteinformationen aktualisiert wurden
    for geraet in Geraet.geraete:
        if geraet[2] == "NaN" and geraet[3] == "NaN":
            fehlerhafte_geraete.append((geraet, "Falsches Gerät oder Module"))

    return fehlerhafte_geraete

def ButtenCheck(baudrate_var, anzahl_var, boards_var, widerstaende_var):
    fehlerhafte_variablen = []
    
    if not baudrate_var.get().isdigit() or int(baudrate_var.get()) < 1:
        fehlerhafte_variablen.append("Baudrate")
    if not anzahl_var.get().isdigit() or int(anzahl_var.get()) < 1:
        fehlerhafte_variablen.append("Anzahl der Geräte")
    if not boards_var.get().isdigit() or int(boards_var.get()) < 1:
        fehlerhafte_variablen.append("Anzahl der Boards")
    if not widerstaende_var.get().isdigit() or int(widerstaende_var.get()) < 1:
        fehlerhafte_variablen.append("Widerstände pro Board")

    return fehlerhafte_variablen

def print_geräte_check(baudrate_var, anzahl_var, boards_var, widerstaende_var, show_window_if_no_errors=False):
    baudrate = int(baudrate_var.get())
    fehlerhafte_geraete = geräte_check(baudrate)
    fehlerhafte_variablen = ButtenCheck(baudrate_var, anzahl_var, boards_var, widerstaende_var)
    
    fehlerhafte_konfigurationen = []
    if not fehlerhafte_geraete and not fehlerhafte_variablen:
        fehlerhafte_konfigurationen.append(("Alles", "Alle Geräte und Variablen sind korrekt konfiguriert."))
    else:
        for geraet, fehler in fehlerhafte_geraete:
            fehlerhafte_konfigurationen.append((f"Gerät: {geraet}", f"Fehler: {fehler}"))
        for variable in fehlerhafte_variablen:
            fehlerhafte_konfigurationen.append((f"Variable: {variable}", "ist nicht korrekt konfiguriert."))
    
    if fehlerhafte_geraete or fehlerhafte_variablen or show_window_if_no_errors:
        show_output_window(fehlerhafte_konfigurationen)
        return True  # Fehler gefunden, Fenster geöffnet
    
    return False  # Keine Fehler gefunden, Fenster nicht geöffnet

def show_output_window(fehlerhafte_konfigurationen):
    window = tk.Toplevel()
    window.title("Ausgabe der Gerätekonfigurationen")

    main_frame = ttk.Frame(window, padding="10")
    main_frame.pack(expand=True, fill='both')

    tree = ttk.Treeview(main_frame, columns=("Kategorie", "Beschreibung"), show="headings")
    tree.heading("Kategorie", text="Kategorie")
    tree.heading("Beschreibung", text="Beschreibung")
    tree.column("Kategorie", anchor=tk.W, width=300)
    tree.column("Beschreibung", anchor=tk.W, width=500)

    for kategorie, beschreibung in fehlerhafte_konfigurationen:
        tree.insert("", "end", values=(kategorie, beschreibung))

    tree.pack(expand=True, fill='both')

    # Fenstergröße anpassen und zentrieren
    window.update_idletasks()
    window.geometry(f'{window.winfo_reqwidth()}x{window.winfo_reqheight()}+{int(window.winfo_screenwidth()/2 - window.winfo_reqwidth()/2)}+{int(window.winfo_screenheight()/2 - window.winfo_reqheight()/2)}')

    # Füge einen Button zum Schließen des Fensters hinzu
    close_button = ttk.Button(main_frame, text="Schließen", command=window.destroy)
    close_button.pack(pady=(10, 0))
