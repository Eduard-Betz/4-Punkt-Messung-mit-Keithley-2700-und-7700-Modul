#PlotsConrols.py

import time  # Importiert das Zeitmodul, um Zeitfunktionen zu verwenden
import tkinter as tk  # Importiert das tkinter-Modul für die GUI-Erstellung
import matplotlib.pyplot as plt
import threading  # Importiert das threading-Modul für parallele Ausführung von Aufgaben

from tkinter import ttk  # Importiert das ttk-Modul von tkinter für erweiterte Widgets
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Importiert das Modul zur Integration von Matplotlib in Tkinter
from matplotlib.figure import Figure  # Importiert das Figure-Objekt von Matplotlib zur Erstellung von Diagrammen

from global_vars import Messwerte, gefundenen_geraete, BoardConfig, Plotwerte  # Importiert globale Variablen und Konfigurationen aus anderen Modulen


# Globale debugging_PlotsConrole-Variable
debugging_PlotsConrole = False

def debug_print(message):
    if debugging_PlotsConrole:
        print(message)

debug_print("Debugging aktiviert")

OHM = '\u03A9'  # Unicode für das Ohm-Zeichen, wird zur Darstellung von Widerstandseinheiten verwendet

# Entry-Widgets-Struktur
entry_widgets = {}


def update_plotwerte(plots_data):
    debug_print("DEBUG: update_plotwerte wird aufgerufen.")
    """
    Aktualisiert die Plots und die Board Controls automatisch, wenn neue Plotwerte vorhanden sind.
    """
    plotter1 = plots_data.get('plotter1')
    plotter2 = plots_data.get('plotter2')
    plotwerte = Plotwerte.get_plotwerte()  # Holt die neuen Plotwerte
    board_vars = plots_data.get('board_vars', {})

    debug_print("DEBUG: Rufe update_plots auf.")
    update_plots(plotter1, plotter2, plotwerte, board_vars, plots_data)

    #debug_print("DEBUG: Starte Aktualisierung der Board-Controls. Aktuelle Plotwerte: " + str(plotwerte))
    update_board_controls(plots_data)

    # Aktualisiere die Legende für die beiden Plotter (Temperatur und Widerstand)
    if plotter1 and plotter2:
        debug_print("DEBUG: Aktualisiere die Legende für Plotter.")
        handles, labels = plotter1.get_legend_handles_labels()
        plotter1.legend(handles=handles, labels=labels, loc='center left', bbox_to_anchor=(1, 0.5))

        handles, labels = plotter2.get_legend_handles_labels()
        plotter2.legend(handles=handles, labels=labels, loc='center left', bbox_to_anchor=(1, 0.5))

        debug_print("DEBUG: Legenden wurden aktualisiert.")


def clear_existing_plots(plotter1, plotter2, plots_data):
    debug_print("DEBUG: clear_existing_plots wird aufgerufen.")
    """
    Löscht alle bestehenden Plots und ihre Daten von den Achsenobjekten.
    """
    debug_print("Lösche bestehende Plots")

    if plotter1:
        plotter1.clear()  # Lösche die Achsen für plotter1
        plotter1.figure.canvas.draw_idle()
    if plotter2:
        plotter2.clear()  # Lösche die Achsen für plotter2
        plotter2.figure.canvas.draw_idle()

    if 'plotter1_points' in plots_data:
        plots_data['plotter1_points'].clear()
    if 'plotter2_points' in plots_data:
        plots_data['plotter2_points'].clear()


def clear_plots_and_controls(plots_data):
    debug_print("DEBUG: clear_plots_and_controls wird aufgerufen.")
    """
    Löscht alle bestehenden Plot- und Board-Controls.
    """
    debug_print("Lösche bestehende Plots und Controls")

    for tab in plots_data['control_notebook'].winfo_children():
        tab.destroy()

    plots_data['plotter1'] = None
    plots_data['plotter2'] = None
    plots_data['board_vars'].clear()

    if 'entry_widgets' in plots_data:
        plots_data['entry_widgets'].clear()


def create_plot(tab, relx, rely, relwidth, relheight, title, xlabel, ylabel):
    debug_print("DEBUG: create_plot wird aufgerufen.")
    """
    Erstellt ein Plot-Widget und fügt es zu einem Tab hinzu, mit einer korrekten Beschriftung und
    optimierter Platzierung für die Legende.
    """
    fig = Figure(figsize=(8, 4), dpi=100)  # Vergrößere die Figur für mehr Platz
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.get_tk_widget().place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

    fig.tight_layout(pad=2)  # Mehr Platz für die Ränder
    fig.subplots_adjust(right=0.75)  # Platz für die Legende rechts lassen

    return ax


def plot_update_thread(plotter1, plotter2, plots_data):
    debug_print("DEBUG: plot_update_thread wird aufgerufen.")
    """
    Überwacht kontinuierlich, ob neue Messwerte vorhanden sind, und aktualisiert die Plots und Board-Controls.
    """
    last_update_len = len(Messwerte)

    while True:
        if len(Messwerte) > last_update_len:
            print(f"Neue Messwerte hinzugekommen: {len(Messwerte) - last_update_len}")
            last_update_len = len(Messwerte)

            debug_print("DEBUG: Rufe umwandeln_in_plotwerte auf.")
            Plotwerte.umwandeln_in_plotwerte(Messwerte)

            plot_werte = Plotwerte.get_plotwerte()
            #debug_print(f"DEBUG: Plotwerte nach Umwandlung: {plot_werte}")

            if plot_werte:
                update_plots(plotter1, plotter2, plot_werte, plots_data['board_vars'], plots_data)
                update_board_controls(plots_data)  # Hier sicherstellen, dass auch die Board Controls aktualisiert werden

        time.sleep(0.1)  # Warte kurz, um die CPU nicht zu belasten



def get_dynamic_colormap(num_boards):
    debug_print("DEBUG: get_dynamic_colormap wird aufgerufen.")
    """
    Gibt eine Liste von Farben zurück, die für alle Boards verwendet werden können.
    """
    cmap = plt.get_cmap('viridis')
    colors = [cmap(i / num_boards) for i in range(num_boards)]
    return colors






def toggle_board_visibility(board_nummer, var, plotter1, plotter2, plots_data):
    debug_print(f"DEBUG: toggle_board_visibility aufgerufen für Board {board_nummer}. Status: {var.get()}")
    """
    Steuert die Sichtbarkeit der Plots für das jeweilige Board.
    """
    if var.get():
        plots_data['board_vars'][board_nummer] = True
    else:
        plots_data['board_vars'][board_nummer] = False

    # Aktualisiere die Plots nach dem Umschalten der Checkbox
    plot_werte = Plotwerte.get_plotwerte()
    update_plots(plotter1, plotter2, plot_werte, plots_data['board_vars'], plots_data)

def update_board_controls(plots_data):
    debug_print("DEBUG: update_board_controls wird aufgerufen.")
    """
    Aktualisiert die Board-Steuerelemente mit den neuesten Messwerten.
    """
    plot_werte = Plotwerte.get_plotwerte()
    #debug_print(f"DEBUG: Starte Aktualisierung der Board-Controls. Aktuelle Plotwerte: {plot_werte}")

    for board_nr, (checkbox_wert, widerstand_data) in plot_werte.items():
        if checkbox_wert:
            for widerstand_nr, (temperatur_true, werte) in widerstand_data.items():
                last_value = next((v for v in reversed(werte['values']) if v is not None and v is not False), None)

                debug_print(f"DEBUG: Board {board_nr}, Widerstand {widerstand_nr}, letzter gültiger Wert: {last_value}")

                if last_value is not None:
                    label_name = f"temp_{board_nr}_{widerstand_nr}" if temperatur_true else f"res_{board_nr}_{widerstand_nr}"

                    if label_name in plots_data['entry_widgets']:
                        entry = plots_data['entry_widgets'][label_name]
                        debug_print(f"DEBUG: Versuche, Wert {last_value} in Widget '{label_name}' zu schreiben.")

                        entry.config(state='normal')
                        entry.delete(0, tk.END)
                        entry.insert(0, str(last_value))
                        entry.config(state='readonly')

                        debug_print(f"DEBUG: Wert {last_value} erfolgreich in Widget '{label_name}' eingetragen.")
                    else:
                        debug_print(f"DEBUG: Kein Widget '{label_name}' gefunden für Board {board_nr}, Widerstand {widerstand_nr}.")
                else:
                    debug_print(f"DEBUG: Kein gültiger Wert vorhanden für Board {board_nr}, Widerstand {widerstand_nr}.")


def update_plots(plotter1, plotter2, plot_werte, board_vars, plots_data):
    debug_print("DEBUG: update_plots wird aufgerufen.")
    """
    Aktualisiert die Plots basierend auf den neuesten Plotwerten und sorgt dafür,
    dass die Farben und die Legende statisch bleibt, nur die Sichtbarkeit der Boards verändert wird.
    """
    if plotter1 is None or plotter2 is None:
        raise ValueError("Plotter sind nicht initialisiert.")

    num_boards = int(gefundenen_geraete.get_variable('boards'))
    widerstaende_pro_board = int(gefundenen_geraete.get_variable('widerstaende'))

    # Farben für Boards aus der globalen Variable plots_data beibehalten
    if 'plot_colors' not in plots_data:
        if num_boards == 0:
            print("Keine Boards vorhanden, überspringe das Update.")
            return

        # Farben dynamisch für jedes Board zuweisen und speichern
        colors = get_dynamic_colormap(num_boards)
        plots_data['plot_colors'] = colors

        # Legende einmalig festlegen (festes Layout mit allen Boards)
        for board_nr in range(1, num_boards + 1):
            for widerstand_nr in range(1, widerstaende_pro_board + 1):
                color = colors[board_nr - 1]
                label = f"Board: {board_nr},{widerstand_nr}"

                # Dummy-Plots erstellen, um die Legende zu definieren
                if widerstand_nr % 2 == 0:
                    plotter1.scatter([], [], color=color, label=label)
                else:
                    plotter2.scatter([], [], color=color, label=label)

        # Einmalige Festlegung der Legende
        plotter1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plotter2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    else:
        # Farben aus der vorherigen Initialisierung beibehalten
        colors = plots_data['plot_colors']

    # Lösche nur die Daten in den Plots (aber nicht die Achsen/Legenden)
    plotter1.clear()
    plotter2.clear()

    # Achsenbeschriftungen bei jedem Update sicherstellen
    plotter1.set_title("Widerstände")
    plotter1.set_xlabel("Zeit (s)")
    plotter1.set_ylabel(f"Widerstand ({OHM})")

    plotter2.set_title("Temperatur")
    plotter2.set_xlabel("Zeit (s)")
    plotter2.set_ylabel("Temperatur (°C)")

    # Plot-Daten dynamisch aktualisieren, basierend auf den Checkbox-Werten
    for board_nr, (checkbox_wert, widerstand_data) in plot_werte.items():
        color = colors[board_nr - 1]  # Feste Farbe für das Board
        alpha_value = 1.0 if board_vars.get(board_nr, False) else 0.2  # Sichtbarkeit ändern

        for widerstand_nr, (temperatur_true, werte) in widerstand_data.items():
            time_data = werte["time"]
            value_data = werte["values"]

            if temperatur_true:
                plotter = plotter2  # Temperaturplot
            else:
                plotter = plotter1  # Widerstandsplot

            plotter.scatter(time_data, value_data, color=color, alpha=alpha_value, label=f"Board {board_nr},{widerstand_nr}")

    # Achsen und Legenden nach dem Update wieder anzeigen
    plotter1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plotter2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plotter1.figure.canvas.draw_idle()
    plotter2.figure.canvas.draw_idle()






def create_and_start_plots(plots_data, from_loaded_data=False):
    debug_print("DEBUG: create_and_start_plots wird aufgerufen.")
    """
    Erstellt und startet die Plots und die zugehörigen Board-Controls.
    """
    clear_existing_plots(plots_data.get('plotter1'), plots_data.get('plotter2'), plots_data)

    if 'entry_widgets' not in plots_data:
        plots_data['entry_widgets'] = {}

    anzahl_boards = int(gefundenen_geraete.get_variable('boards'))
    widerstaende_pro_board = int(gefundenen_geraete.get_variable('widerstaende'))

    if anzahl_boards == 0:
        print("Keine Boards gefunden")
        return

    # Erstelle die Plots
    plots_data['plotter1'] = create_plot(
        plots_data['control_notebook'].master, 0, 0, 0.4, 0.5,
        title="Widerstände", xlabel="Zeit (s)", ylabel=f"Widerstand ({OHM})"
    )
    plots_data['plotter2'] = create_plot(
        plots_data['control_notebook'].master, 0, 0.5, 0.4, 0.5,
        title="Temperatur", xlabel="Zeit (s)", ylabel="Temperatur (°C)"
    )

    # Hole die Plotwerte, falls vorhanden
    plot_werte = Plotwerte.get_plotwerte()

    boards = range(1, anzahl_boards + 1)
    tabs_required = (anzahl_boards + 9) // 10

    # Erstelle die Board Controls für jedes Board
    for tab_index in range(tabs_required):
        tab = ttk.Frame(plots_data['control_notebook'])
        plots_data['control_notebook'].add(tab, text=f"Boards {tab_index*10+1}-{min((tab_index+1)*10, anzahl_boards)}")

        for board_index in range(tab_index * 10, min((tab_index + 1) * 10, anzahl_boards)):
            board_nr = board_index + 1
            if board_nr not in plots_data['board_vars']:
                plots_data['board_vars'][board_nr] = tk.BooleanVar(value=True)

            row = board_index % 5
            column = (board_index // 5) % 2

            # Übergebe den neuen Parameter 'from_loaded_data' basierend darauf, ob Daten geladen wurden oder nicht
            board_frame = create_board_controls(
                tab,
                tab,
                board_nr,
                plots_data['board_vars'][board_nr],
                plot_werte,
                plots_data['plotter1'],
                plots_data['plotter2'],
                row,
                plots_data['board_vars'],
                plots_data,
                from_loaded_data  # Entscheidet, ob die Daten aus den geladenen Plotwerten stammen
            )
            board_frame.grid(row=row, column=column, padx=10, pady=10, sticky='nsew')

    # Starte den Plot-Update-Thread
    plot_thread = threading.Thread(target=plot_update_thread, args=(plots_data['plotter1'], plots_data['plotter2'], plots_data))
    plot_thread.daemon = True
    plot_thread.start()

    # Initiales Update der Plotwerte nach dem Laden oder dem Start
    update_plotwerte(plots_data)


def create_board_controls(tab, frame, board_nummer, var, plot_werte, plotter1, plotter2, index, board_vars, plots_data, from_loaded_data=False):
    """
    Erstellt die Steuerungselemente für ein bestimmtes Board im GUI und gibt das erstellte Frame zurück.
    
    :param from_loaded_data: Gibt an, ob die Daten aus geladenen Plotwerten (True) oder aus Metadaten (False) stammen.
    """
    debug_print(f"DEBUG: create_board_controls wird aufgerufen für Board {board_nummer}.")
    
    board_frame = tk.Frame(frame, bd=2, relief=tk.RIDGE)
    board_frame.grid(row=index, column=0, sticky='nsew', padx=5, pady=5)

    checkbox = tk.Checkbutton(board_frame, text=f"Board {board_nummer}", variable=var,
                              command=lambda: toggle_board_visibility(board_nummer, var, plotter1, plotter2, plots_data))
    checkbox.grid(row=0, column=0, columnspan=3, sticky='w', padx=5, pady=5)

    board_vars[board_nummer] = var

    # Erstelle Board Controls basierend auf Metadaten (bei neuen Messungen)
    #elif BoardConfig.get_board_config():
    if BoardConfig.get_board_config():
        debug_print(f"DEBUG: Erstelle Board Controls basierend auf Metadaten für Board {board_nummer}.")
        for config in BoardConfig.get_board_config():
            if config[0] == board_nummer:
                widerstand_nr = config[1]
                temperatur_true = config[4]

                row = len(plots_data.get('entry_widgets', {})) + 1

                if temperatur_true:
                    label_text = f"Temperatur ({widerstand_nr}) :"
                    unit_text = "°C"
                    label_name = f"temp_{board_nummer}_{widerstand_nr}"
                else:
                    label_text = f"Widerstand ({widerstand_nr}) :"
                    unit_text = OHM
                    label_name = f"res_{board_nummer}_{widerstand_nr}"

                label = tk.Label(board_frame, text=label_text, anchor='e')
                label.grid(row=row, column=0, sticky='e', padx=5, pady=2)

                entry = tk.Entry(board_frame, state='readonly', width=10)
                entry.grid(row=row, column=1, padx=5, pady=2)

                unit_label = tk.Label(board_frame, text=unit_text, anchor='w')
                unit_label.grid(row=row, column=2, sticky='w', padx=5, pady=2)

                plots_data['entry_widgets'][label_name] = entry

    return board_frame
