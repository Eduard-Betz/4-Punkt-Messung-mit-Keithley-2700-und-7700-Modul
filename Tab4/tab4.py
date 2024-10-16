# Datei: tab4.py

import tkinter as tk
from tkinter import ttk
from time import sleep

from global_vars import PlotAuswahl, TK_Fehler
from Tab4.Data_to_excel import print_tk_data
from Tab4.TKPlot import (
    plot_resistance_vs_temperature,
    plot_resistance_vs_avg_temperature,
    fit_and_store_line_data,
    fit_and_store_line_data_avg_temperature
)

from Tab4.AuswahlTK import open_widerstand_window
from Tab4.TKPlotControls import create_multiple_boards

# Debug-Flag definieren
debug_Tab4 = False  # Debug-Ausgaben sind standardmäßig deaktiviert

# Debug-Ausgabefunktion
def debug_print(*args, **kwargs):
    if debug_Tab4:
        print(*args, **kwargs)


def create_tab4(notebook):
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="Tab 4")

    # Frame für den ersten und zweiten Plot
    plot_frame1 = tk.Frame(tab4)
    plot_frame1.place(relx=0.01, relwidth=0.38, relheight=0.5)
    plot_frame2 = tk.Frame(tab4)
    plot_frame2.place(relx=0.01, rely=0.5, relwidth=0.38, relheight=0.5)

    # Notebook für die Boards innerhalb von tab4
    boards_notebook = ttk.Notebook(tab4)
    boards_notebook.place(relx=0.40, relwidth=0.4, relheight=1)  # Platzierung neben den Plotframes

    # Funktion zum Löschen der Plots und Zurücksetzen der Daten
    def clear_plots_and_data():
        # Lösche den Inhalt von plot_frame1 und plot_frame2
        for widget in plot_frame1.winfo_children():
            widget.destroy()  # Entferne alle Widgets innerhalb des Frames
        for widget in plot_frame2.winfo_children():
            widget.destroy()

        # Setze die Daten in PlotAuswahl auf None oder eine neutrale Einstellung zurück
        PlotAuswahl.reset_steigung()
        PlotAuswahl.reset_sinkend()

    # Funktion, um das Fenster für die Widerstandsauswahl zu öffnen und dann die Plots zu erstellen
    def open_and_plot():
        # Zuerst die Plots leeren und die Daten zurücksetzen
        clear_plots_and_data()

        # Erstelle ein neues Fenster für die Widerstandsauswahl
        window = tk.Toplevel()

        # Öffne das Fenster und pausiere die Ausführung bis das Fenster geschlossen ist
        open_widerstand_window(window)
        window.wait_window()  # Warten, bis das Fenster geschlossen ist

        # Erstelle die beiden Plots mit den Daten aus beiden Flanken
        plot_resistance_vs_temperature(plot_frame1, PlotAuswahl.get_steigung(), PlotAuswahl.get_sinkend())
        plot_resistance_vs_avg_temperature(plot_frame2, PlotAuswahl.get_steigung(), PlotAuswahl.get_sinkend())

    # Funktion, um die TK-Berechnung durchzuführen und die Boards anzuzeigen
    def TKBerechnen():
        # Führe die Berechnungen durch und aktualisiere die Plots
        fit_and_store_line_data(plot_frame1, PlotAuswahl.get_steigung(), PlotAuswahl.get_sinkend())
        fit_and_store_line_data_avg_temperature(plot_frame2, PlotAuswahl.get_steigung(), PlotAuswahl.get_sinkend())

        sleep(0.1)
        # Lösche die Tabs im boards_notebook, bevor neue erstellt werden
        for tab in boards_notebook.tabs():
            boards_notebook.forget(tab)

        # Erstellen der Board-Controls mit Tabs
        create_multiple_boards(boards_notebook)

    # Erstelle die Buttons
    button_positions = [
        # Dieser Button öffnet zuerst die Auswahl, löscht Plots, setzt Daten zurück und erstellt dann neue Plots
        ("Plot erstellen", 0, open_and_plot),
        ("TK Berechnen", 0.1, TKBerechnen),
        ("TK zu Exel Tabelle", 0.8, print_tk_data),
        ("R^2 Ausgeben", 0.9, print_r_squared_values)
    ]

    buttons = create_buttons(tab4, button_positions)

    # Rückgabe des tab4
    return tab4

def create_buttons(tab, button_positions):
    buttons = []
    for text, rel_y, command in button_positions:
        button = tk.Button(tab, text=text, command=command)
        button.place(relx=1, rely=rel_y, anchor='ne', relwidth=0.2, relheight=0.1)
        buttons.append(button)
    return buttons


    
# Funktion zum Ausgeben der R²-Werte im Terminal
def print_r_squared_values():
    fehler_variablen = TK_Fehler.fehler_variablen
    if not fehler_variablen:
        print("Keine R²-Werte verfügbar. Bitte führen Sie zuerst die TK-Berechnung durch.")
        return
    for board_nr, resistors in fehler_variablen.items():
        for resistor_nr, data in resistors.items():
            print(f"\nBoard {board_nr}, Widerstand {resistor_nr}:")
            # Normaldaten
            normal_data = data.get('normal', {})
            r_squared_steigend = normal_data.get('r_squared_steigend', 'N/A')
            r_squared_sinkend = normal_data.get('r_squared_sinkend', 'N/A')
            print("  Normale Temperaturen:")
            print(f"    R² Steigend: {r_squared_steigend}")
            print(f"    R² Sinkend: {r_squared_sinkend}")
            # Gemittelte Daten
            avg_data = data.get('avg', {})
            r_squared_steigend_avg = avg_data.get('r_squared_steigend', 'N/A')
            r_squared_sinkend_avg = avg_data.get('r_squared_sinkend', 'N/A')
            print("  Durchschnittliche Temperaturen:")
            print(f"    R² Steigend: {r_squared_steigend_avg}")
            print(f"    R² Sinkend: {r_squared_sinkend_avg}")
