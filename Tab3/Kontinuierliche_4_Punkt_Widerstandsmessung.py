# Kontinuierliche_4_Punkt_Widerstandsmessung.py

import serial
from global_vars import gefundenen_geraete

# Globale debugging_KontinuierlicheMessung-Variable
debugging_KontinuierlicheMessung = False

def debug_print(message):
    if debugging_KontinuierlicheMessung:
        print(message)

def send_command(ser, command):
    try:
        ser.write((command + '\n').encode())  # Befehl senden
        response = ser.read_until().decode().strip()  # Antwort lesen
        debug_print(f"Befehl gesendet: {command}, Antwort erhalten: {response}")  # Debugging-Ausgabe
        return response
    except Exception as e:
        debug_print(f"Fehler beim Senden des Befehls '{command}': {e}")
        return ""

def messe_widerstand(board_nummer, widerstand_nummer, schnittstelle, kanal, temp_umwandlung, sensor, stop_event):
    """
    Führt eine Widerstandsmessung durch und gibt das Ergebnis zurück.
    Überprüft nach jedem Schritt, ob das Stop-Ereignis gesetzt wurde.
    """
    baudrate = gefundenen_geraete.get_variable('baudrate')
    try:
        # Seriellen Port öffnen
        with serial.Serial(
            port=schnittstelle,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.3
        ) as ser:
            if stop_event.is_set():
                debug_print("Messung gestoppt während der Initialisierung.")
                return None

            send_command(ser, 'ROUTe:OPEN:ALL')
            if stop_event.is_set():
                debug_print("Messung gestoppt nach ROUTe:OPEN:ALL.")
                return None

            send_command(ser, f'ROUTe:CLOSe (@{kanal})')
            if stop_event.is_set():
                debug_print(f"Messung gestoppt nach ROUTe:CLOSe (@{kanal}).")
                return None

            send_command(ser, 'FUNCtion "FRES"')
            if stop_event.is_set():
                debug_print("Messung gestoppt nach FUNCtion 'FRES'.")
                return None

            send_command(ser, 'FORMat:ELEMents READing')
            if stop_event.is_set():
                debug_print("Messung gestoppt nach FORM:ELEMENTS READING.")
                return None

            response = send_command(ser, 'FETCh?')
            if stop_event.is_set():
                debug_print("Messung gestoppt nach FETCh?.")
                return None

            measurement = float(response) if response else None
            if measurement is not None and measurement < 0:
                measurement = -measurement  # Korrektur bei negativen Werten

            # Debugging: Ausgabe des gemessenen Werts
            debug_print(f"Gemessener Widerstand für Board {board_nummer}, Widerstand {widerstand_nummer}: {measurement}")

            return {
                'board_nummer': board_nummer,
                'widerstand_nummer': widerstand_nummer,
                'gemessener_widerstand': measurement,
                'temp_umwandlung': temp_umwandlung,
                'sensor': sensor
            }
    except Exception as e:
        debug_print(f"Fehler bei der Messung: {e}")
        return None
