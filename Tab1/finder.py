# finder.py
# Finder Klasse zur Kommunikation mit den Keithley Geräten über RS-232

import serial

#debugging Print
debugging = False

def debug_print(message):
    if debugging:
        print(message)


class Finder:
    def __init__(self, baudrate):
        self.baudrate = baudrate

    def find_device(self, port):
        try:
            debug_print(f"Versuche Verbindung zu {port}")
            with serial.Serial(port, self.baudrate, timeout=1) as ser:
                ser.write(b'*IDN?\r\n')
                idn_response = ser.readline().decode().strip()
                debug_print(f"Antwort von {port}: {idn_response}")
                
                if not idn_response or 'KEITHLEY' not in idn_response.upper():
                    return None, 'NaN', 'NaN'

                idn_parts = idn_response.split(',')
                if len(idn_parts) > 1:
                    idn = f"Keithley: {idn_parts[1].strip()}"
                else:
                    idn = "Keithley: Unbekanntes Modell"

                ser.write(b'*OPT?\r\n')
                opt = ser.readline().decode().strip()
                debug_print(f"Optionen von {port}: {opt}")
                mod1 = '7700' if '7700' in opt.split(',')[0] else 'NaN'
                mod2 = '7700' if '7700' in opt.split(',')[1] else 'NaN'

                return idn, mod1, mod2

        except serial.SerialException as e:
            debug_print(f"Fehler beim Öffnen des Ports {port}: {e}")
            return None, 'NaN', 'NaN'

        except Exception as e:
            debug_print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
            return None, 'NaN', 'NaN'
