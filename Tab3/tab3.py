# tab3.py

import tkinter as tk
from tkinter import ttk
import threading

from global_vars import Zeitverzögertemessung, Zeitverzögerungswert, Messwerte, Plotwerte # Import der globalen Variablen

from Tab3.Messungen import start_measurement
from Tab3.PlotsControls import create_and_start_plots
from Tab3.SpeichernLaden import user_save_to_csv, load_file


debugging = False
# Event für das Stoppen der Messung
stop_event = threading.Event()
measurement_thread = None  # Globale Variable für den Messungs-Thread

def update_and_print_globals(delay_var, time_var):
    global Zeitverzögertemessung, Zeitverzögerungswert
    Zeitverzögertemessung = delay_var.get()
    Zeitverzögerungswert = time_var.get()
    print(f"Checkbox geändert: Zeitverzögertemessung = {Zeitverzögertemessung}")
    print(f"Zeit geändert: Zeitverzögerungswert = {Zeitverzögerungswert}")

def create_tab3(notebook, switch_to_tab4_callback):
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Tab 3")

    plots_data = {
        'control_notebook': ttk.Notebook(tab3),
        'board_vars': {},
        'data_vars': {},
        'plotter1': None,
        'plotter2': None
    }
    plots_data['control_notebook'].place(relx=0.4, rely=0, relwidth=0.4, relheight=1.0)

    delay_var = tk.BooleanVar(value=Zeitverzögertemessung)
    time_var = tk.StringVar(value=Zeitverzögerungswert)

    def toggle_time_entry():
        if delay_var.get():
            time_entry.config(state='normal')
        else:
            time_entry.config(state='disabled')
        update_and_print_globals(delay_var, time_var)

    def format_time(event=None):
        value = time_var.get().replace(":", "")
        if value.isdigit() and len(value) > 2:
            minutes = value[:-2]
            seconds = value[-2:]
            formatted_time = f"{minutes}:{seconds}"
            time_var.set(formatted_time)
        elif value.isdigit() and len(value) <= 2:
            time_var.set(value)
        time_entry.icursor(tk.END)
        update_and_print_globals(delay_var, time_var)

    delay_var.trace_add('write', lambda *args: update_and_print_globals(delay_var, time_var))
    time_var.trace_add('write', lambda *args: update_and_print_globals(delay_var, time_var))

    delay_frame = ttk.LabelFrame(tab3, text="Zeitverzögerung für die Messungen")
    delay_frame.place(relx=1, rely=0.2, anchor='ne', relwidth=0.2, relheight=0.1)

    checkbox = tk.Checkbutton(delay_frame, variable=delay_var, command=toggle_time_entry)
    checkbox.pack(side=tk.LEFT, padx=50, pady=10)

    time_entry = tk.Entry(delay_frame, textvariable=time_var, state='disabled', width=8)
    time_entry.pack(side=tk.RIGHT, padx=50, pady=10)

    time_entry.bind("<FocusOut>", format_time)
    time_entry.bind("<Return>", format_time)
    time_entry.bind("<KeyRelease>", format_time)

    buttons = [
        ("Starten", 0, lambda: start_messungen_with_print(delay_var, time_var, plots_data)),
        ("Stop", 0.1, stop_messungen),
        ("Speichern", 0.7, user_save_to_csv),
        ("Laden", 0.8, lambda: load_with_print(plots_data)),  # Hier die Debug-Funktion für Laden
        ("Weiter", 0.9, switch_to_tab4_callback)  # Übergabe der Funktion zum Wechsel zu Tab 4
    ]

    for text, rel_y, command in buttons:
        button = tk.Button(tab3, text=text, command=command)
        button.place(relx=1, rely=rel_y, anchor='ne', relwidth=0.2, relheight=0.1)

    return plots_data

def start_messungen_with_print(delay_var, time_var, plots_data):
    update_and_print_globals(delay_var, time_var)
    # Vor dem Start sicherstellen, dass die Werte aktualisiert sind und ausgeben
    print(f"Vor dem Start der Messung: Zeitverzögertemessung = {Zeitverzögertemessung}, Zeitverzögerungswert = {Zeitverzögerungswert}")
    start_messungen(delay_var.get(), time_var.get(), plots_data)

def start_messungen(Zeitverzögertemessung, Zeitverzögerungswert, plots_data):
    global measurement_thread
    create_and_start_plots(plots_data)
    stop_event.clear()
    measurement_thread = threading.Thread(target=start_measurement, args=(stop_event, Zeitverzögertemessung, Zeitverzögerungswert))
    measurement_thread.start()

def stop_messungen():
    global measurement_thread
    stop_event.set()
    if measurement_thread is not None and measurement_thread.is_alive():
        measurement_thread.join()
    print("Messung gestoppt.")



def load_with_print(plots_data):
    #print("DEBUG: Vor dem Aufruf von load_file")
    if debugging:
        load_file(plots_data)
        print("Messwerte")
        print(Messwerte)
        print("Plotwerte")
        print(Plotwerte.get_plotwerte())
    else:
        load_file(plots_data)
    #print("DEBUG: Nach dem Aufruf von load_file")