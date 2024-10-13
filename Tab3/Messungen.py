#Messungen.py

import time

from global_vars import gefundenen_geraete, BoardConfig, Messwerte  # Messwerte und weitere Variablen importieren

from Tab3.Kontinuierliche_4_Punkt_Widerstandsmessung import messe_widerstand
from Tab3.Widerstand_zu_Temperatur import resistance_to_temperature
from Tab3.SpeichernLaden import create_csv_file, save_to_csv

# Lokale Debugging-Variable für diese Datei
debugging_messungen = False

def debug_print_messungen(message):
    if debugging_messungen:
        print(message)
        

def start_measurement(stop_event, Zeitverzögertemessung, Zeitverzögerungswert):
    debug_print_messungen("Messung wird gestartet...")
    start_time = time.time()

    # Prüfe und zeige den Status der verzögerten Messung und den Verzögerungswert an
    debug_print_messungen(f"Zeitverzögertemessung: {Zeitverzögertemessung}")
    debug_print_messungen(f"Zeitverzögerungswert: {Zeitverzögerungswert}")

    # Wenn die Zeitverzögertemessung aktiviert ist, zeige die Wartezeit an
    if Zeitverzögertemessung:
        debug_print_messungen(f"Zeitverzögerte Messung aktiviert. Wartezeit zwischen den Durchläufen: {Zeitverzögerungswert} Minuten.")

    # CSV-Datei erstellen
    file_name = create_csv_file()
    if not file_name:
        debug_print_messungen("Fehler beim Erstellen der CSV-Datei. Messung wird abgebrochen.")
        return

    boards = int(gefundenen_geraete.get_variable('boards'))
    widerstaende = int(gefundenen_geraete.get_variable('widerstaende'))

    while not stop_event.is_set():
        # Führe eine vollständige Messung aller Boards durch
        for board_nummer in range(1, boards + 1):
            Aktuell_gemessenes_board = []

            # Hole die Konfiguration für das aktuelle Board
            board_config = [config for config in BoardConfig.get_board_config() if config[0] == board_nummer]

            for config in board_config:
                widerstand_nummer = config[1]
                schnittstelle, kanal, temp_true, sensor_type = config[2], config[3], config[4], config[5]

                zeit = round(time.time() - start_time, 2)

                # Führe die Messung durch
                ergebnis = messe_widerstand(board_nummer, widerstand_nummer, schnittstelle, kanal, temp_true, sensor_type, stop_event)

                if ergebnis and ergebnis.get('gemessener_widerstand') is not None:
                    widerstand = round(ergebnis['gemessener_widerstand'], 2)

                    if temp_true:
                        temp_value = resistance_to_temperature(widerstand, sensor_type)
                        temp_value = round(temp_value, 2) if isinstance(temp_value, (int, float)) else False
                    else:
                        temp_value = False

                    debug_print_messungen(f"DEBUG: Board {board_nummer}, Widerstand {widerstand_nummer}, Widerstand: {widerstand}, Temperatur: {temp_value}")

                    Aktuell_gemessenes_board.append([zeit, board_nummer, widerstand_nummer, schnittstelle, kanal, temp_true, sensor_type, widerstand, temp_value])
                else:
                    debug_print_messungen(f"Keine gültige Messung für Board {board_nummer}, Widerstand {widerstand_nummer}. Ergebnis: {ergebnis}")
                    Aktuell_gemessenes_board.append([zeit, board_nummer, widerstand_nummer, schnittstelle, kanal, temp_true, sensor_type, None, False])

            # Speichere die Ergebnisse des aktuellen Boards in der CSV-Datei
            save_to_csv(file_name, Aktuell_gemessenes_board)

            Messwerte.extend(Aktuell_gemessenes_board)  # Messwerte speichern
            Aktuell_gemessenes_board.clear()

            if stop_event.is_set():
                debug_print_messungen("Messung gestoppt.")
                break

        # Wenn die Zeitverzögertemessung aktiv ist, warte die angegebene Zeit vor dem nächsten Durchlauf
        if Zeitverzögertemessung:
            debug_print_messungen(f"Warte {Zeitverzögerungswert}, bevor die nächste Messung beginnt...")
            minutes, seconds = map(int, Zeitverzögerungswert.split(':'))
            delay = minutes * 60 + seconds  # Zeit in Sekunden berechnen
            for i in range(delay):
                if stop_event.is_set():
                    print("Messung während der Verzögerung gestoppt.")
                    break
                print(f"Wartezeit: {delay - i} Sekunden verbleibend...")
                time.sleep(1)  # Warte eine Sekunde und überprüfe das Stop-Event

    debug_print_messungen("Messung abgeschlossen.")

def stop_measurement(stop_event):
    debug_print_messungen("Messung wird gestoppt...")
    if stop_event:
        stop_event.set()
    debug_print_messungen("Messung gestoppt.")
