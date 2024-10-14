# Datei: TKPlot.py
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from global_vars import TKBoardVariabeln

from Tab3.PlotsControls import get_dynamic_colormap

debugging_TKPlot = False

def debug_print(message):
    if debugging_TKPlot:
        print(message)

def calculate_avg_temperatures(flanken_auswahl):
    """
    Berechnet die durchschnittlichen Temperaturen basierend auf der Position der Messpunkte im Array.
    Messpunkte an derselben Position in den Arrays der verschiedenen Boards werden zusammengefasst.
    """
    if flanken_auswahl is None or not flanken_auswahl[0]:
        return []  # Keine gültigen Daten, leere Liste zurückgeben

    selected_data = flanken_auswahl[1]

    # Finde die maximale Anzahl an Messpunkten (Positionen) über alle Boards hinweg
    num_measurements = max([len(board_data) for board_nr, (checkbox, board_data) in selected_data.items() if checkbox], default=0)
    
    avg_temperatures = []

    # Berechne den Durchschnitt für jede Position (basierend auf dem Index im Array)
    for i in range(num_measurements):
        temps = []
        for board_nr, (checkbox, board_data) in selected_data.items():
            if checkbox and i < len(board_data):
                # Nimm den Temperaturwert an der Position i
                _, _, temperature = board_data[i]
                if temperature is not None:
                    temps.append(temperature)
        
        # Berechne den Durchschnitt der gültigen Temperaturen für diesen Messpunkt (Position i)
        if temps:
            avg_temperatures.append(sum(temps) / len(temps))  # Durchschnitt berechnen
        else:
            avg_temperatures.append(None)  # Keine gültigen Temperaturwerte für diese Messung

    return avg_temperatures

def plot_resistance_vs_temperature_generic(plot_frame, steigung_auswahl, sinkend_auswahl, use_avg_temperatures=False):
    """
    Generische Funktion zum Plotten von Widerstand vs. Temperatur oder Durchschnittstemperatur.
    """
    fig = Figure(figsize=(8.5, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Boards sammeln
    steigung_boards = set(steigung_auswahl[1].keys()) if steigung_auswahl and steigung_auswahl[0] else set()
    sinkend_boards = set(sinkend_auswahl[1].keys()) if sinkend_auswahl and sinkend_auswahl[0] else set()
    all_boards = steigung_boards.union(sinkend_boards)

    if not all_boards:
        debug_print("Keine Boards zum Plotten gefunden.")
        return  # Nichts zu plotten, also beenden

    colors = get_dynamic_colormap(len(all_boards))  # Hole Farben für die eindeutigen Boards
    board_color_map = {board_nr: colors[i] for i, board_nr in enumerate(sorted(all_boards, key=lambda x: int(str(x).replace('Board ', ''))))}

    plotted_boards = set()  # Set, um nachzuverfolgen, welche Boards bereits gelabelt wurden

    # Funktion zum Plotten der Flanke
    def plot_flanke(flanken_auswahl, avg_temperatures=None):
        if not flanken_auswahl[0]:
            debug_print("Keine gültigen Daten für diese Flanke.")
            return

        for board_nr, (checkbox, selected_values) in flanken_auswahl[1].items():
            if checkbox:
                valid_temperatures = []
                valid_resistances = []
                for idx, (time, resistance, temperature) in enumerate(selected_values):
                    temp = None
                    if use_avg_temperatures:
                        if avg_temperatures and idx < len(avg_temperatures):
                            temp = avg_temperatures[idx]
                    else:
                        temp = temperature
                    if resistance is not None and temp is not None:
                        valid_temperatures.append(temp)
                        valid_resistances.append(resistance)

                if valid_temperatures and valid_resistances:
                    # Verwende die Farbe und setze das Label nur, wenn das Board noch nicht geplottet wurde
                    if board_nr not in plotted_boards:
                        board_nr_str = str(board_nr).replace('Board ', '')
                        label = f"Board {board_nr_str}"
                        ax.scatter(valid_temperatures, valid_resistances, label=label, color=board_color_map[board_nr], marker='o')
                        plotted_boards.add(board_nr)
                    else:
                        ax.scatter(valid_temperatures, valid_resistances, color=board_color_map[board_nr], marker='o')

    # Berechne Durchschnittstemperaturen falls erforderlich
    avg_temperatures_steigend = calculate_avg_temperatures(steigung_auswahl) if use_avg_temperatures and steigung_auswahl and steigung_auswahl[0] else []
    avg_temperatures_sinkend = calculate_avg_temperatures(sinkend_auswahl) if use_avg_temperatures and sinkend_auswahl and sinkend_auswahl[0] else []

    # Plotten der steigenden und sinkenden Flanke
    if steigung_auswahl and steigung_auswahl[0]:
        plot_flanke(steigung_auswahl, avg_temperatures_steigend)
    if sinkend_auswahl and sinkend_auswahl[0]:
        plot_flanke(sinkend_auswahl, avg_temperatures_sinkend)

    # Achsenbeschriftungen und Titel
    x_label = 'Durchschnittliche Temperatur (°C)' if use_avg_temperatures else 'Temperatur (°C)'
    ax.set_xlabel(x_label)
    ax.set_ylabel('Widerstand (Ohm)')
    title = 'Widerstand vs. Durchschnittliche Temperatur für alle Boards' if use_avg_temperatures else 'Widerstand vs. Temperatur für alle Boards'
    ax.set_title(title)

    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), borderaxespad=0)

    fig.tight_layout(rect=[0.01, 0, 0.95, 1])

    for widget in plot_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

def fit_and_store_line_data_generic(plot_frame, steigung_auswahl, sinkend_auswahl, use_avg_temperatures=False):
    """
    Generische Funktion zum Berechnen der linearen Regression und Speichern der Ergebnisse.
    """
    def fit_line(temperatures, resistances):
        if len(temperatures) < 2 or len(resistances) < 2:
            return None, (None, None)
        m, b = np.polyfit(temperatures, resistances, 1)
        temp_bereich = (round(min(temperatures), 2), round(max(temperatures), 2))
        return round(m, 5), temp_bereich

    fig = Figure(figsize=(8.5, 4), dpi=100)
    ax = fig.add_subplot(111)

    steigung_boards = set(steigung_auswahl[1].keys()) if steigung_auswahl and steigung_auswahl[0] else set()
    sinkend_boards = set(sinkend_auswahl[1].keys()) if sinkend_auswahl and sinkend_auswahl[0] else set()
    all_boards = steigung_boards.union(sinkend_boards)

    if not all_boards:
        print("Keine Boards gefunden.")
        return

    colors = get_dynamic_colormap(len(all_boards))
    board_color_map = {board_nr: colors[i] for i, board_nr in enumerate(sorted(all_boards, key=lambda x: int(str(x).replace('Board ', ''))))}

    plotted_boards = set()

    # Berechne Durchschnittstemperaturen falls erforderlich
    avg_temperatures_steigend = calculate_avg_temperatures(steigung_auswahl) if use_avg_temperatures and steigung_auswahl and steigung_auswahl[0] else []
    avg_temperatures_sinkend = calculate_avg_temperatures(sinkend_auswahl) if use_avg_temperatures and sinkend_auswahl and sinkend_auswahl[0] else []

    # Runden der Durchschnittstemperaturen auf zwei Dezimalstellen
    if use_avg_temperatures:
        avg_temperatures_steigend = [round(temp, 2) for temp in avg_temperatures_steigend if temp is not None]
        avg_temperatures_sinkend = [round(temp, 2) for temp in avg_temperatures_sinkend if temp is not None]

    # Entferne den Aufruf von TKBoardVariabeln.clear() hier
    # TKBoardVariabeln.clear()  # Dies wird jetzt in den spezifischen Funktionen gehandhabt

    board_results = []

    for board_nr in sorted(all_boards, key=lambda x: int(str(x).replace('Board ', ''))):
        board_nr_str = str(board_nr).replace('Board ', '')  # Entfernt 'Board ' aus board_nr
        resistor_nr = '1'  # Passen Sie dies an, wenn mehrere Widerstände vorhanden sind

        temperatures_steigend, resistances_steigend = [], []
        temperatures_sinkend, resistances_sinkend = [], []

        # Steigende Flanke
        if steigung_auswahl and board_nr in steigung_auswahl[1]:
            for idx, (time, resistance, temperature) in enumerate(steigung_auswahl[1][board_nr][1]):
                temp = None
                if use_avg_temperatures:
                    if avg_temperatures_steigend and idx < len(avg_temperatures_steigend):
                        temp = avg_temperatures_steigend[idx]
                else:
                    temp = temperature
                if resistance is not None and temp is not None:
                    temperatures_steigend.append(temp)
                    resistances_steigend.append(resistance)

        # Sinkende Flanke
        if sinkend_auswahl and board_nr in sinkend_auswahl[1]:
            for idx, (time, resistance, temperature) in enumerate(sinkend_auswahl[1][board_nr][1]):
                temp = None
                if use_avg_temperatures:
                    if avg_temperatures_sinkend and idx < len(avg_temperatures_sinkend):
                        temp = avg_temperatures_sinkend[idx]
                else:
                    temp = temperature
                if resistance is not None and temp is not None:
                    temperatures_sinkend.append(temp)
                    resistances_sinkend.append(resistance)

        # Runden der Temperaturwerte auf zwei Dezimalstellen
        temperatures_steigend = [round(temp, 2) for temp in temperatures_steigend]
        temperatures_sinkend = [round(temp, 2) for temp in temperatures_sinkend]

        # Berechnung der Steigungen und Temperaturbereiche
        steigung_steigend, temp_bereich_steigend = fit_line(temperatures_steigend, resistances_steigend)
        steigung_sinkend, temp_bereich_sinkend = fit_line(temperatures_sinkend, resistances_sinkend)

        # Kombinierte Temperaturen für Temp. min und Temp. max (für die GUI)
        all_temperatures = temperatures_steigend + temperatures_sinkend
        if all_temperatures:
            temp_min = round(min(all_temperatures), 5)
            temp_max = round(max(all_temperatures), 5)
        else:
            temp_min = temp_max = "N/A"

        # Speichern der Werte in TKBoardVariabeln
        if not use_avg_temperatures:
            # Hier nicht mehr clear aufrufen, sondern die Daten hinzufügen
            TKBoardVariabeln.update_board(
                board_nr_str,
                resistor_nr,
                steigung_steigend, temp_bereich_steigend,
                steigung_sinkend, temp_bereich_sinkend,
                temp_min, temp_max
            )
        else:
            TKBoardVariabeln.update_board_avg(
                board_nr_str,
                resistor_nr,
                steigung_steigend, temp_bereich_steigend,
                steigung_sinkend, temp_bereich_sinkend
            )

        # Ergebnisse sammeln für die Ausgabe
        board_results.append({
            'board_nr': int(board_nr_str),
            'steigung_steigend': steigung_steigend,
            'temp_bereich_steigend': temp_bereich_steigend,
            'steigung_sinkend': steigung_sinkend,
            'temp_bereich_sinkend': temp_bereich_sinkend
        })

        # Funktion zum Plotten der gefitteten Linie
        def plot_fitted_line(temperatures, resistances, color):
            if len(temperatures) > 1 and len(resistances) > 1:
                m, b = np.polyfit(temperatures, resistances, 1)
                x_vals = np.array([min(temperatures), max(temperatures)])
                y_vals = m * x_vals + b
                ax.plot(x_vals, y_vals, color=color, linestyle='--', linewidth=2)

        # Plotten der Linien
        plot_fitted_line(temperatures_steigend, resistances_steigend, board_color_map[board_nr])
        plot_fitted_line(temperatures_sinkend, resistances_sinkend, board_color_map[board_nr])

    # Ergebnisse sortieren und ausgeben
    for result in board_results:
        debug_print(f"Board {result['board_nr']}:")
        debug_print(f"  Steigende Flanke{' (durchschn. Temp.)' if use_avg_temperatures else ''}: Steigung = {result['steigung_steigend']}, Temperaturbereich = {result['temp_bereich_steigend']}")
        debug_print(f"  Sinkende Flanke{' (durchschn. Temp.)' if use_avg_temperatures else ''}: Steigung = {result['steigung_sinkend']}, Temperaturbereich = {result['temp_bereich_sinkend']}")

    # Funktion zum Plotten der Flankenpunkte
    def plot_flanke(flanken_auswahl, avg_temperatures=None):
        if not flanken_auswahl[0]:
            print("Keine gültigen Daten für diese Flanke.")
            return

        for board_nr, (checkbox, selected_values) in flanken_auswahl[1].items():
            if checkbox:
                valid_temperatures = []
                valid_resistances = []
                for idx, (time, resistance, temperature) in enumerate(selected_values):
                    temp = None
                    if use_avg_temperatures:
                        if avg_temperatures and idx < len(avg_temperatures):
                            temp = avg_temperatures[idx]
                    else:
                        temp = temperature
                    if resistance is not None and temp is not None:
                        valid_temperatures.append(temp)
                        valid_resistances.append(resistance)

                if valid_temperatures and valid_resistances:
                    if board_nr not in plotted_boards:
                        board_nr_str = str(board_nr).replace('Board ', '')
                        label = f"Board {board_nr_str}"
                        ax.scatter(valid_temperatures, valid_resistances, label=label, color=board_color_map[board_nr], marker='o')
                        plotted_boards.add(board_nr)
                    else:
                        ax.scatter(valid_temperatures, valid_resistances, color=board_color_map[board_nr], marker='o')

    # Plotten der Flankenpunkte
    if steigung_auswahl and steigung_auswahl[0]:
        if use_avg_temperatures:
            plot_flanke(steigung_auswahl, avg_temperatures_steigend)
        else:
            plot_flanke(steigung_auswahl)
    if sinkend_auswahl and sinkend_auswahl[0]:
        if use_avg_temperatures:
            plot_flanke(sinkend_auswahl, avg_temperatures_sinkend)
        else:
            plot_flanke(sinkend_auswahl)

    # Achsenbeschriftungen und Titel
    x_label = 'Durchschnittliche Temperatur (°C)' if use_avg_temperatures else 'Temperatur (°C)'
    ax.set_xlabel(x_label)
    ax.set_ylabel('Widerstand (Ohm)')
    title = 'Widerstand vs. Durchschnittliche Temperatur für alle Boards' if use_avg_temperatures else 'Widerstand vs. Temperatur für alle Boards'
    ax.set_title(title)

    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), borderaxespad=0)

    fig.tight_layout(rect=[0.01, 0, 0.95, 1])

    for widget in plot_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

# Funktionen zum Aufrufen der generischen Funktionen mit spezifischen Parametern
def plot_resistance_vs_temperature(plot_frame, steigung_auswahl, sinkend_auswahl):
    plot_resistance_vs_temperature_generic(plot_frame, steigung_auswahl, sinkend_auswahl, use_avg_temperatures=False)

def plot_resistance_vs_avg_temperature(plot_frame, steigung_auswahl, sinkend_auswahl):
    plot_resistance_vs_temperature_generic(plot_frame, steigung_auswahl, sinkend_auswahl, use_avg_temperatures=True)

def fit_and_store_line_data(plot_frame, steigung_auswahl, sinkend_auswahl):
    # Vor dem Aufruf der generischen Funktion nicht mehr TKBoardVariabeln.clear() aufrufen
    fit_and_store_line_data_generic(plot_frame, steigung_auswahl, sinkend_auswahl, use_avg_temperatures=False)

def fit_and_store_line_data_avg_temperature(plot_frame, steigung_auswahl, sinkend_auswahl):
    # Hier ebenfalls nicht mehr TKBoardVariabeln.clear() aufrufen
    fit_and_store_line_data_generic(plot_frame, steigung_auswahl, sinkend_auswahl, use_avg_temperatures=True)
