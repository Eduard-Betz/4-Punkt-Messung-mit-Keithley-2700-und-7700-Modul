# ReconnectBoard.py
import tkinter as tk
from tkinter import messagebox
from Tab1.finder import Finder
from global_vars import BoardConfig, Geraet, gefundenen_geraete

def reconnect_devices(parent):
    finder = Finder(gefundenen_geraete.get_variable('baudrate'))
    errors = []

    def update_port(geraet_nummer, new_port):
        for idx, geraet in enumerate(Geraet.geraete):
            if geraet[0] == geraet_nummer:
                Geraet.geraete[idx] = (geraet_nummer, new_port, geraet[2], geraet[3])
                Geraet.notify_callbacks()
                return

    def check_ports():
        ports = [geraet[1] for geraet in Geraet.geraete]
        found_devices = {}
        for port in ports:
            idn, mod1, mod2 = finder.find_device(port)
            if idn:
                found_devices[port] = (idn, mod1, mod2)
        return found_devices

    found_devices = check_ports()

    for geraet in Geraet.geraete:
        geraet_nummer = geraet[0]
        port = geraet[1]
        expected_mod1 = geraet[2]
        expected_mod2 = geraet[3]

        if port in found_devices:
            idn, mod1, mod2 = found_devices[port]
            if mod1 != expected_mod1 or mod2 != expected_mod2:
                errors.append(f"Module an Port {port} stimmen nicht überein. Erwartet: {expected_mod1}, {expected_mod2}. Gefunden: {mod1}, {mod2}.")
        else:
            new_port = None
            for new_port_candidate, device_info in found_devices.items():
                idn, mod1, mod2 = device_info
                if idn and (mod1 == expected_mod1 or mod2 == expected_mod2):
                    new_port = new_port_candidate
                    update_port(geraet_nummer, new_port)
                    break
            if not new_port:
                errors.append(f"Gerät {geraet_nummer} nicht gefunden.")

    # Überprüfe die Board-Konfigurationen und aktualisiere die Ports
    for board in BoardConfig.get_board_config():
        port = board[2]
        channel = board[3]
        geraet_nummer = board[0]

        if port in found_devices:
            idn, mod1, mod2 = found_devices[port]
            multiplexer = int(channel / 100)
            channel_number = channel % 100

            if (multiplexer == 1 and mod1 == 'NaN') or (multiplexer == 2 and mod2 == 'NaN'):
                errors.append(f"Ausgewählter Kanal {channel} an Port {port} ist ungültig für Board {board[0]} Widerstand {board[1]}.")
        else:
            errors.append(f"Gerät an Port {port} für Board {board[0]} Widerstand {board[1]} nicht gefunden.")

    if errors:
        message = "\n".join(errors)
        messagebox.showerror("Fehler beim Initialisieren", message, parent=parent)
    else:
        messagebox.showinfo("Erfolg", "Gerät neu initialisiert. Alle Ports korrekt.", parent=parent)
