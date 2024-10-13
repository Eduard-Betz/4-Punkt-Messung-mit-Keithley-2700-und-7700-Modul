#PeichernLaden.yp

import csv
from datetime import datetime
from tkinter import filedialog, Tk

from global_vars import Messwerte, gefundenen_geraete, BoardConfig, Plotwerte # Importiere den PlotwerteManager und globale Variablen

from Tab3.PlotsControls import create_and_start_plots, clear_plots_and_controls, update_plots

# Globale debugging_SpeichernLaden-Variable
debugging_SpeichernLaden = False

letzte_plotzeiten = {}  # Initialisiere es als leeres Dictionary

def debug_print(message):
    if debugging_SpeichernLaden:
        print(message)


def create_csv_file():
    timestamp = datetime.now().strftime("%d_%m_%y__%H_%M")
    file_name = f"Messung_{timestamp}.csv"
    
    # Werte aus gefundenen_geraete hinzufügen
    geraete_data = [
        ["Baudrate", gefundenen_geraete.variables['baudrate']],
        ["Anzahl_der_geraete", gefundenen_geraete.variables['anzahl']],
        ["Anzahl_der_Boards", gefundenen_geraete.variables['boards']],
        ["Widerstaende_pro_Board", gefundenen_geraete.variables['widerstaende']],
        ["Gefundene_Geraete"]
    ]
    geraete_data.extend(gefundenen_geraete.geraete)
    
    header = [["Zeit", "Board Nr", "Widerstand Nr", "Port", "Kannal", "Temperatur True/False", "Sensor", "Gemessener Widerstand", "Temperaturwert"]]
    
    try:
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(geraete_data)  # Speichere die gefundenen Geräte und Variablen
            writer.writerows(header)  # Speichere den Header
        print(f"CSV-Datei {file_name} wurde erstellt.")
        return file_name
    except Exception as e:
        print(f"Fehler beim Erstellen der CSV-Datei {file_name}: {e}")
        return None

def save_to_csv(file_name, data):
    try:
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        print(f"Daten in {file_name} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Daten in {file_name}: {e}")


def user_save_to_csv():
    try:
        # Öffne Dateidialog, um den Speicherort und Namen auszuwählen
        root = Tk()
        root.withdraw()  # Verstecke das Hauptfenster
        file_name = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        root.destroy()  # Schließe das Tkinter-Hauptfenster

        if file_name:
            # Werte aus gefundenen_geraete hinzufügen
            geraete_data = [
                ["Baudrate", gefundenen_geraete.variables['baudrate']],
                ["Anzahl_der_geraete", gefundenen_geraete.variables['anzahl']],
                ["Anzahl_der_Boards", gefundenen_geraete.variables['boards']],
                ["Widerstaende_pro_Board", gefundenen_geraete.variables['widerstaende']],
                ["Gefundene_Geraete"]
            ]
            geraete_data.extend(gefundenen_geraete.geraete)
            
            header = [["Zeit", "Board Nr", "Widerstand Nr", "Port", "Kannal", "Temperatur True/False", "Sensor", "Gemessener Widerstand", "Temperaturwert"]]
            
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(geraete_data)  # Speichere die gefundenen Geräte und Variablen
                writer.writerows(header)  # Speichere den Header

                # Messwerte verarbeiten und in CSV speichern
                for messung in Messwerte:
                    zeit = messung[0]
                    board_nr = messung[1]
                    widerstand_nr = messung[2]
                    port = messung[3]
                    kanal = messung[4]
                    temperatur_true = messung[5]
                    sensor = messung[6]
                    widerstand = messung[7] if messung[7] is not None else "False"
                    temperaturwert = messung[8] if messung[8] is not None else "False"
                    
                    # Schreibe die verarbeiteten Messwerte in die CSV
                    writer.writerow([zeit, board_nr, widerstand_nr, port, kanal, temperatur_true, sensor, widerstand, temperaturwert])
            
            debug_print(f"Daten in {file_name} gespeichert.")
        else:
            debug_print("Speichern abgebrochen.")
    except Exception as e:
        debug_print(f"Fehler beim Speichern der Daten: {e}")


"""""
def load_file(plots_data):
    try:
        # Schritt 1: Vor dem Laden die bisherigen Werte löschen
        Messwerte.clear()  # Messwerte zurücksetzen
        Plotwerte.clear_plotwerte()  # Plotwerte zurücksetzen
        BoardConfig.update_board_config([])  # Leere Board-Konfiguration

        # Lösche die bestehenden GUI-Elemente (Tabs und Plots)
        clear_plots_and_controls(plots_data)

        # Schritt 2: Öffne einen Dateidialog, um die CSV-Datei auszuwählen
        root = Tk()
        root.withdraw()  # Verstecke das Hauptfenster
        file_name = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        root.destroy()  # Schließe das Tkinter-Hauptfenster

        if file_name:
            # Schritt 3: Datei öffnen und Zeilen auslesen
            with open(file_name, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                all_rows = list(reader)

                # Überprüfen, ob die Datei ausreichend Zeilen enthält
                if len(all_rows) < 6:
                    raise ValueError("Die CSV-Datei hat nicht genügend Daten.")

                # Schritt 4: Geräteeinstellungen aus den ersten Zeilen laden
                gefundenen_geraete.variables['baudrate'] = all_rows[0][1]
                gefundenen_geraete.variables['anzahl'] = all_rows[1][1]
                gefundenen_geraete.variables['boards'] = all_rows[2][1]
                gefundenen_geraete.variables['widerstaende'] = all_rows[3][1]

                # Schritt 5: Gefundene Geräte laden (Daten nach "Gefundene_Geraete")
                gefundenen_geraete.geraete.clear()
                board_config_start_index = None
                for idx, row in enumerate(all_rows[5:]):
                    if row[0] == "Zeit":  # Wenn "Zeit" erreicht wird, beginnen die Messwerte
                        board_config_start_index = idx + 5  # Speichere den Startpunkt der Messdaten
                        break
                    gefundenen_geraete.geraete.append(row)

                # Schritt 6: BoardConfig laden (falls in der CSV vorhanden)
                BoardConfig.update_board_config([])  # Leere die BoardConfig
                if board_config_start_index is not None:
                    for row in all_rows[5:board_config_start_index]:
                        # Überprüfen, ob die Konfiguration valide ist (z.B. keine leeren Zeilen)
                        if len(row) >= 2:
                            BoardConfig.update_board_config(row)  # Füge die BoardConfig hinzu

                # Schritt 7: Messwerte laden (nach den Gerätedaten)
                Messwerte.clear()
                for row in all_rows[board_config_start_index + 1:]:
                    try:
                        time_value = float(row[0]) if row[0] else 0.0
                        board_nr = int(row[1])
                        widerstand_nr = int(row[2])
                        temperatur_true = row[5].lower() == 'true'
                        resistance_value = float(row[7]) if row[7] and row[7].lower() != 'false' else None
                        temperature_value = float(row[8]) if row[8] and row[8].lower() != 'false' else None

                        # Füge die Messwerte zur globalen Messwertliste hinzu
                        Messwerte.append([time_value, board_nr, widerstand_nr, row[3], row[4], temperatur_true, row[6], resistance_value, temperature_value])

                    except ValueError as e:
                        print(f"Fehler beim Konvertieren der Werte in Zeile: {row}. Fehler: {e}")
                        continue
                

                # Daten erfolgreich geladen
                debug_print(f"Geräte, BoardConfig und Messwerte aus {file_name} erfolgreich geladen.")

                Plotwerte.umwandeln_in_plotwerte(Messwerte)

                #plot_werte = Plotwerte.get_plotwerte()
                #debug_print(f"DEBUG: Plotwerte nach Umwandlung: {plot_werte}")
                
                # Daten erfolgreich geladen
                debug_print(f"Geräte, BoardConfig und Messwerte aus {file_name} erfolgreich geladen.")

                # Schritt 8: Plot- und Board-Steuerelemente neu initialisieren
               # create_and_start_plots(plots_data, from_loaded_data=True)

                # Schritt 9: Plots aktualisieren
               # update_plots(plots_data['plotter1'], plots_data['plotter2'], Plotwerte.get_plotwerte(), plots_data['board_vars'], plots_data)

            def print_all_info():
                # Ausgabe der Geräteinformationen
                print("Gefundenen Geräte:")
            for geraet in gefundenen_geraete.geraete:
                print(geraet)

                print("\nVariablen:")
            for key, value in gefundenen_geraete.variables.items():
                print(f"{key}: {value}")

            # Ausgabe der Board-Konfiguration
            print("\nBoard-Konfiguration:")
            board_config = BoardConfig.get_board_config()
            if not board_config:
                print("Keine Board-Konfiguration gefunden.")
            else:
                for config in board_config:
                    print(config)

            # Beispielaufruf der Funktion
            print_all_info()


        else:
            print("Laden abgebrochen.")
    except Exception as e:
        print(f"Fehler beim Laden der Datei: {e}")
"""

'''
def extract_board_config(all_rows, board_config_start_index, widerstaende_pro_board):
    """
    Extrahiert die Board-Konfiguration aus den gegebenen Zeilen ab dem Startpunkt.

    :param all_rows: Die vollständige Liste der Zeilen aus der CSV-Datei
    :param board_config_start_index: Der Index, an dem die Board-Konfiguration beginnt
    :param widerstaende_pro_board: Die Anzahl der Widerstände pro Board
    :return: Eine Liste der Board-Konfigurationen
    """
    board_config = []
    for i in range(board_config_start_index, len(all_rows)):
        row = all_rows[i]
        if len(row) >= 5:  # Stelle sicher, dass genügend Spalten vorhanden sind
            try:
                board_nr = int(row[1])
                widerstand_nr = int(row[2])
                port = row[3]
                kanal = int(row[4])
                temperatur_true = row[5].lower() == 'true'
                sensor = row[6] if len(row) > 6 else False

                # Erstellen des Konfigurationseintrags
                board_config.append([board_nr, widerstand_nr, port, kanal, temperatur_true, sensor])
                
                # Maximale Anzahl an Konfigurationen basierend auf der Anzahl der Boards und Widerstände pro Board
                if len(board_config) >= (10 * widerstaende_pro_board):  # max 10 Boards, each with the specified number of resistors
                    break
            except ValueError:
                continue
    return board_config
'''

def extract_board_config(all_rows, board_config_start_index, widerstaende_pro_board, anzahl_boards):
    """
    Extrahiert die Board-Konfiguration aus den gegebenen Zeilen ab dem Startpunkt.

    :param all_rows: Die vollständige Liste der Zeilen aus der CSV-Datei
    :param board_config_start_index: Der Index, an dem die Board-Konfiguration beginnt
    :param widerstaende_pro_board: Die Anzahl der Widerstände pro Board
    :param anzahl_boards: Die Anzahl der Boards
    :return: Eine Liste der Board-Konfigurationen
    """
    board_config = []
    for i in range(board_config_start_index, len(all_rows)):
        row = all_rows[i]
        if len(row) >= 5:  # Stelle sicher, dass genügend Spalten vorhanden sind
            try:
                board_nr = int(row[1])
                widerstand_nr = int(row[2])
                port = row[3]
                kanal = int(row[4])
                temperatur_true = row[5].lower() == 'true'
                sensor = row[6] if len(row) > 6 else False

                # Erstellen des Konfigurationseintrags
                board_config.append([board_nr, widerstand_nr, port, kanal, temperatur_true, sensor])
                
                # Dynamische Begrenzung basierend auf der tatsächlichen Anzahl der Boards
                if len(board_config) >= (anzahl_boards * widerstaende_pro_board):
                    break
            except ValueError:
                continue
    return board_config

# Beispiel für die Integration in die load_file Funktion
def load_file(plots_data):
    try:
        # Schritt 1: Vor dem Laden die bisherigen Werte löschen
        Messwerte.clear()
        Plotwerte.clear_plotwerte()
        BoardConfig.update_board_config([])

        # Lösche die bestehenden GUI-Elemente
        clear_plots_and_controls(plots_data)

        # Datei öffnen und Zeilen auslesen
        root = Tk()
        root.withdraw()
        file_name = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        root.destroy()

        if file_name:
            with open(file_name, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                all_rows = list(reader)

                if len(all_rows) < 6:
                    raise ValueError("Die CSV-Datei hat nicht genügend Daten.")

                # Schritt 4: Geräteeinstellungen aus den ersten Zeilen laden
                gefundenen_geraete.variables['baudrate'] = all_rows[0][1]
                gefundenen_geraete.variables['anzahl'] = all_rows[1][1]
                gefundenen_geraete.variables['boards'] = all_rows[2][1]
                gefundenen_geraete.variables['widerstaende'] = all_rows[3][1]

                # Schritt 5: Gefundene Geräte laden
                gefundenen_geraete.geraete.clear()
                board_config_start_index = None
                for idx, row in enumerate(all_rows[5:]):
                    if row[0] == "Zeit":
                        board_config_start_index = idx + 5
                        break
                    gefundenen_geraete.geraete.append(row)

                # Schritt 6: BoardConfig laden
                #BoardConfig.update_board_config([])
                if board_config_start_index is not None:
                    board_config = extract_board_config(all_rows, board_config_start_index, int(gefundenen_geraete.variables['widerstaende']),int(gefundenen_geraete.variables['boards']))
                    BoardConfig.update_board_config(board_config)

                # Schritt 7: Messwerte laden
                Messwerte.clear()
                for row in all_rows[board_config_start_index + 1:]:
                    try:
                        time_value = float(row[0]) if row[0] else 0.0
                        board_nr = int(row[1])
                        widerstand_nr = int(row[2])
                        temperatur_true = row[5].lower() == 'true'
                        resistance_value = float(row[7]) if row[7] and row[7].lower() != 'false' else None
                        temperature_value = float(row[8]) if row[8] and row[8].lower() != 'false' else None

                        Messwerte.append([time_value, board_nr, widerstand_nr, row[3], row[4], temperatur_true, row[6], resistance_value, temperature_value])

                    except ValueError as e:
                        print(f"Fehler beim Konvertieren der Werte in Zeile: {row}. Fehler: {e}")
                        continue

                debug_print(f"Geräte, BoardConfig und Messwerte aus {file_name} erfolgreich geladen.")
                Plotwerte.umwandeln_in_plotwerte(Messwerte)

                # Daten erfolgreich geladen
                debug_print(f"Geräte, BoardConfig und Messwerte aus {file_name} erfolgreich geladen.")


                # Schritt 8: Plot- und Board-Steuerelemente neu initialisieren
                create_and_start_plots(plots_data, from_loaded_data=False)

                # Schritt 9: Plots aktualisieren
                update_plots(plots_data['plotter1'], plots_data['plotter2'], Plotwerte.get_plotwerte(), plots_data['board_vars'], plots_data)



            def print_all_info():
                print("Gefundenen Geräte:")
                for geraet in gefundenen_geraete.geraete:
                    print(geraet)

                print("\nVariablen:")
                for key, value in gefundenen_geraete.variables.items():
                    print(f"{key}: {value}")

                print("\nBoard-Konfiguration:")
                #board_config = BoardConfig.get_board_config()
                if not board_config:
                    print("Keine Board-Konfiguration gefunden.")
                else:
                    for config in board_config:
                        print(config)
                        

            if debugging_SpeichernLaden:
                print_all_info()
                #print(Messwerte)
        else:
            print("Laden abgebrochen.")
    except Exception as e:
        print(f"Fehler beim Laden der Datei: {e}")

