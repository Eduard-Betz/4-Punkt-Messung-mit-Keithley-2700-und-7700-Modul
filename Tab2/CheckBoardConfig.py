# CheckBoardConfig.py
import tkinter as tk
from global_vars import BoardConfig

def check_board_config():
    board_config = BoardConfig.get_board_config()
    not_configured_errors = []
    pt_not_selected_errors = []
    duplicate_errors = {}
    config_set = {}
    
    for config in board_config:
        board_num, resistor_num, port, channel, pt_enabled, pt_value = config
        
        # Check if the resistor is configured
        if port == 'Unknown' or channel in [None, 0]:
            not_configured_errors.append(f"Board {board_num} Widerstand {resistor_num}")
            continue
        
        # Check if PT is enabled but no PT value is selected
        if pt_enabled and not pt_value:
            pt_not_selected_errors.append(f"Board {board_num} Widerstand {resistor_num}")
        
        # Check for duplicates
        if (port, channel) in config_set:
            duplicate_resistor = config_set[(port, channel)]
            if (port, channel) not in duplicate_errors:
                duplicate_errors[(port, channel)] = [duplicate_resistor]
            duplicate_errors[(port, channel)].append(f"Board {board_num} Widerstand {resistor_num}")
        else:
            config_set[(port, channel)] = f"Board {board_num} Widerstand {resistor_num}"
    
    return not_configured_errors, pt_not_selected_errors, duplicate_errors

def show_check_result(show_all_ok):
    not_configured_errors, pt_not_selected_errors, duplicate_errors = check_board_config()
    all_ok = not not_configured_errors and not pt_not_selected_errors and not duplicate_errors

    if all_ok:
        if show_all_ok:
            message = "Alle Widerstände sind korrekt konfiguriert"
        else:
            return True
    else:
        message = ""
        if duplicate_errors:
            message += "Identische Widerstände\n"
            for resistors in duplicate_errors.values():
                first = True
                for resistor in resistors:
                    if first:
                        message += f"  • {resistor}\n"
                        first = False
                    else:
                        message += f"    {resistor}\n"
                message += "\n"
        if not_configured_errors:
            message += "Nicht konfigurierte Widerstände\n"
            for error in not_configured_errors:
                message += f"  {error}\n"
            message += "\n"
        if pt_not_selected_errors:
            message += "PT nicht ausgewählt\n"
            for error in pt_not_selected_errors:
                message += f"  {error}\n"
            message += "\n"
    
    # Ein neues Fenster erstellen und die Ergebnisse anzeigen
    result_window = tk.Tk()
    result_window.title("Überprüfungsergebnis")

    # Fenstergröße festlegen
    window_width = 400
    window_height = 300

    # Berechne die Position für das Fenster in der Mitte des Bildschirms
    screen_width = result_window.winfo_screenwidth()
    screen_height = result_window.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    result_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    # Ergebnislabel erstellen und hinzufügen
    result_text = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
    result_text.insert(tk.END, message)
    result_text.config(state=tk.DISABLED)

    # Formatierung der Überschriften
    if duplicate_errors:
        start_idx = message.index("Identische Widerstände")
        end_idx = start_idx + len("Identische Widerstände")
        result_text.tag_add("identische_widerstände", f"1.0+{start_idx}c", f"1.0+{end_idx}c")
        result_text.tag_configure("identische_widerstände", justify='center', font=('Arial', 12, 'bold'))

    if not_configured_errors:
        start_idx = message.index("Nicht konfigurierte Widerstände")
        end_idx = start_idx + len("Nicht konfigurierte Widerstände")
        result_text.tag_add("nicht_konfigurierte_widerstände", f"1.0+{start_idx}c", f"1.0+{end_idx}c")
        result_text.tag_configure("nicht_konfigurierte_widerstände", justify='center', font=('Arial', 12, 'bold'))

    if pt_not_selected_errors:
        start_idx = message.index("PT nicht ausgewählt")
        end_idx = start_idx + len("PT nicht ausgewählt")
        result_text.tag_add("pt_nicht_ausgewählt", f"1.0+{start_idx}c", f"1.0+{end_idx}c")
        result_text.tag_configure("pt_nicht_ausgewählt", justify='center', font=('Arial', 12, 'bold'))

    result_text.pack(expand=True, fill='both')

    result_window.mainloop()

    return all_ok
