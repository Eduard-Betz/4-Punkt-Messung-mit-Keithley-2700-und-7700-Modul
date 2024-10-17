
#AuswahlTK.py

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from global_vars import Plotwerte, PlotAuswahl  # Importiere den PlotwerteManager und PlotAuswahl

from Tab3.PlotsControls import get_dynamic_colormap

debugging_AuswahlTK = False

def debug_print(message):
    if debugging_AuswahlTK:
        print(message)

def create_window(window=None, phase="steigend"):
    if window is None:
        window = tk.Toplevel()
    window.title("Auswahl für die steigende Flanke" if phase == "steigend" else "Auswahl für die sinkende Flanke")
    return window

def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()

def setup_plot_window(plot_frame, plot_werte, phase):
    num_boards = len([board for board, (checkbox, _) in plot_werte.items() if checkbox])
    colors = get_dynamic_colormap(num_boards)  # Farbliste für die Anzahl der Boards
    fig = Figure(figsize=(8.5, 6), dpi=100)

    # Subplot für Widerstandswerte (oben)
    ax1 = fig.add_subplot(211)
    # Subplot für Temperaturwerte (unten)
    ax2 = fig.add_subplot(212)

    all_times = []

    color_index = 0
    for board_nr, (checkbox, widerstand_data) in plot_werte.items():
        if checkbox:
            for widerstand_nr, (is_temperature, data) in widerstand_data.items():
                if not is_temperature:  # Widerstandswerte plotten
                    time_values, resistance_values = data['time'], data['values']
                    valid_times = [time for time, res in zip(time_values, resistance_values) if res not in [None, False]]
                    valid_resistances = [res for res in resistance_values if res not in [None, False]]
                    all_times.extend(valid_times)

                    if valid_times and valid_resistances:
                        # Farbe mit Modulo-Operation verwenden, um den Index in den Bereich der Farben zu halten
                        ax1.scatter(valid_times, valid_resistances, label=f"{board_nr}", color=colors[color_index % len(colors)], marker='o')
                        color_index += 1

                else:  # Temperaturwerte plotten
                    time_values, temp_values = data['time'], data['values']
                    valid_times = [time for time, temp in zip(time_values, temp_values) if temp not in [None, False]]
                    valid_temps = [temp for temp in temp_values if temp not in [None, False]]
                    all_times.extend(valid_times)

                    if valid_times and valid_temps and len(valid_times) == len(valid_temps):
                        # Farbe mit Modulo-Operation verwenden, um den Index in den Bereich der Farben zu halten
                        ax2.scatter(valid_times, valid_temps, label=f"{board_nr}", color=colors[color_index % len(colors)], marker='o')
                        color_index += 1
                    else:
                        debug_print(f"Warnung: Ungültige Daten für Board {board_nr} - Zeiten: {valid_times}, Temperaturen: {valid_temps}")

    return fig, ax1, ax2, all_times

def update_lines(val, slider2_value, canvas, line1_ax1, line2_ax1, line1_ax2, line2_ax2):
    selected_time = float(val)
    line1_ax1.set_xdata([selected_time])
    line1_ax2.set_xdata([selected_time])

    right_time = slider2_value.get()
    if right_time <= selected_time:
        right_time = selected_time + 0.1  # Minimale Verschiebung nach rechts
        slider2_value.set(right_time)
        line2_ax1.set_xdata([right_time])
        line2_ax2.set_xdata([right_time])

    canvas.draw()

def update_right_line(val, slider1_value, slider2_value, canvas, line2_ax1, line2_ax2):
    selected_time = float(val)
    left_time = slider1_value.get()
    if selected_time <= left_time:
        selected_time = left_time + 0.1  # Minimale Verschiebung nach rechts
        slider2_value.set(selected_time)

    line2_ax1.set_xdata([selected_time])
    line2_ax2.set_xdata([selected_time])
    canvas.draw()

def save_selection(phase, slider1_value, slider2_value, plot_werte, save_data=True):
    if not save_data:
        if phase == "steigend":
            PlotAuswahl.update_steigung((False, []))  # Keine Auswahl für steigend
        else:
            PlotAuswahl.update_sinkend((False, []))  # Keine Auswahl für sinkend
        debug_print(f"Keine Auswahl für {phase} gespeichert.")
        return

    x_min = slider1_value.get()
    x_max = slider2_value.get()

    selected_data = {}
    for board_nr, (checkbox, widerstand_data) in plot_werte.items():
        if checkbox:
            temp_values = None
            resistance_values = None
            time_values = None

            for widerstand_nr, (is_temperature, data) in widerstand_data.items():
                if is_temperature:
                    temp_values = data['values']
                    time_values = data['time']
                else:
                    resistance_values = data['values']

            if temp_values and resistance_values and time_values:
                selected_values = [(t, r, temp) for t, r, temp in zip(time_values, resistance_values, temp_values) if x_min <= t <= x_max]
                selected_data[f"Board {board_nr}"] = (checkbox, selected_values)

    if phase == "steigend":
        PlotAuswahl.update_steigung((True, selected_data))
        debug_print(f"Auswahl für steigende Flanke gespeichert: {PlotAuswahl.get_steigung()}")
    else:
        PlotAuswahl.update_sinkend((True, selected_data))
        debug_print(f"Auswahl für sinkende Flanke gespeichert: {PlotAuswahl.get_sinkend()}")

def setup_buttons(window, phase, slider1_value, slider2_value, plot_werte):
    button_frame = tk.Frame(window)
    button_frame.pack(fill="x", pady=10)

    def keine_auswahl():
        if phase == "steigend":
            open_widerstand_window(window, phase="sinkend")
        else:
            save_selection(phase, slider1_value, slider2_value, plot_werte, save_data=False)
            window.destroy()

    keine_auswahl_button = tk.Button(button_frame, text="Keine Auswahl", command=keine_auswahl, bg="#FF9999", fg="black")
    keine_auswahl_button.pack(side="left", padx=10)

    def weiter():
        save_selection(phase, slider1_value, slider2_value, plot_werte)
        if phase == "steigend":
            open_widerstand_window(window, phase="sinkend")
        else:
            window.destroy()

    weiter_button = tk.Button(button_frame, text="Weiter", command=weiter, bg="#99FF99", fg="black")
    weiter_button.pack(side="right", padx=10)

    save_button = tk.Button(window, text="Speichern", command=lambda: save_selection(phase, slider1_value, slider2_value, plot_werte, save_data=True), bg="#CCCCFF", fg="black")
    save_button.place(relx=0.5, rely=0.98, anchor='s')

def open_widerstand_window(window=None, phase="steigend"):
    window = create_window(window, phase)
    clear_window(window)

    plot_frame = tk.Frame(window)
    plot_frame.pack(fill="both", expand=True)

    plot_werte = Plotwerte.get_plotwerte()
    fig, ax1, ax2, all_times = setup_plot_window(plot_frame, plot_werte, phase)
    
    min_time = min(all_times) if all_times else 0
    max_time = max(all_times) if all_times else 1

    # Initiale Linienpositionen
    x_min = min_time
    x_max = max_time

    line1_ax1 = ax1.axvline(x=x_min, color='blue' if phase == "steigend" else 'red', linestyle='--')
    line2_ax1 = ax1.axvline(x=x_max, color='blue' if phase == "steigend" else 'red', linestyle='--')

    line1_ax2 = ax2.axvline(x=x_min, color='blue' if phase == "steigend" else 'red', linestyle='--')
    line2_ax2 = ax2.axvline(x=x_max, color='blue' if phase == "steigend" else 'red', linestyle='--')

    slider_frame = tk.Frame(window)
    slider_frame.pack(fill="x")

    slider1_value = tk.DoubleVar(value=x_min)
    slider2_value = tk.DoubleVar(value=x_max)

    slider1 = tk.Scale(slider_frame, from_=min_time, to=max_time, variable=slider1_value, orient='horizontal', label="Startwert", resolution=0.1, command=lambda val: update_lines(val, slider2_value, canvas, line1_ax1, line2_ax1, line1_ax2, line2_ax2))
    slider1.set(x_min)

    slider2 = tk.Scale(slider_frame, from_=min_time, to=max_time, variable=slider2_value, orient='horizontal', label="Stopwert", resolution=0.1, command=lambda val: update_right_line(val, slider1_value, slider2_value, canvas, line2_ax1, line2_ax2))
    slider2.set(x_max)

    slider1.pack(side="left", fill="x", expand=True)
    slider2.pack(side="left", fill="x", expand=True)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    setup_buttons(window, phase, slider1_value, slider2_value, plot_werte)
