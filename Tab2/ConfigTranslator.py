# ConfigTranslator.py
import tkinter as tk
from global_vars import Geraet

# Definieren des Debug-Flags und der debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def translate_preboard_to_boardconfig(preboard_config):
    board_config = []
    for board in preboard_config:
        if not board['resistors']:  # Wenn keine Widerstände vorhanden sind, überspringen
            continue
        board_num = board['resistors'][0]['board_num']
        for resistor in board['resistors']:
            resistor_num = resistor['resistor_num']
            device_info_str = resistor['selected_device'].get()
            
            if device_info_str and device_info_str.strip():  # Überprüfen, ob das Feld nicht leer ist
                device_info = device_info_str.split('. ')
                if len(device_info) < 3:
                    debug_print(f"Warnung: Ungültiges Geräteformat für Board {board_num}, Widerstand {resistor_num}.")
                    port = 'Unknown'
                    channel = 0
                    pt_enabled = resistor['pt_enabled'].get()
                    pt_value = resistor['selected_pt'].get() if pt_enabled else False
                    board_config.append((board_num, resistor_num, port, channel, pt_enabled, pt_value))
                    continue

                device_number = int(device_info[0])
                multiplexer = int(device_info[1])
                channel_info = device_info[2].split()
                if len(channel_info) < 2:
                    debug_print(f"Warnung: Ungültige Kanalinformation für Board {board_num}, Widerstand {resistor_num}.")
                    port = 'Unknown'
                    channel = 0
                    pt_enabled = resistor['pt_enabled'].get()
                    pt_value = resistor['selected_pt'].get() if pt_enabled else False
                    board_config.append((board_num, resistor_num, port, channel, pt_enabled, pt_value))
                    continue

                channel = int(channel_info[1])

                # Übersetzung der Kanalnummer
                if multiplexer == 1:
                    channel_address = 100 + channel
                elif multiplexer == 2:
                    channel_address = 200 + channel

                # Port des Gerätes
                device = Geraet.get_geraet(device_number)
                port = device[1] if device else 'Unknown'

                # PT-Information
                pt_enabled = resistor['pt_enabled'].get()
                if pt_enabled:
                    pt_value = resistor['selected_pt'].get()
                else:
                    pt_value = False

                # Hinzufügen zur BoardConfig
                board_config.append((board_num, resistor_num, port, channel_address, pt_enabled, pt_value))
            else:
                port = 'Unknown'
                channel = 0
                pt_enabled = resistor['pt_enabled'].get()
                pt_value = resistor['selected_pt'].get() if pt_enabled else False
                board_config.append((board_num, resistor_num, port, channel, pt_enabled, pt_value))
                debug_print(f"Warnung: Kein Gerät für Board {board_num}, Widerstand {resistor_num} ausgewählt.")
    
    return board_config

def translate_boardconfig_to_preboard(board_config):
    preboard_config = []
    boards_dict = {}

    for entry in board_config:
        board_num, resistor_num, port, channel, pt_enabled, pt_value = entry
        if board_num not in boards_dict:
            boards_dict[board_num] = {
                'frame': None,  # Dies wird später zugewiesen
                'resistors': []
            }

        device_number = None
        multiplexer = None
        channel_number = None

        if channel >= 100 and channel < 200:
            multiplexer = 1
            channel_number = channel - 100
        elif channel >= 200 and channel < 300:
            multiplexer = 2
            channel_number = channel - 200

        for device in Geraet.geraete:
            if device[1] == port:  # Gerät anhand des Ports finden
                device_number = device[0]
                break

        selected_device_str = f"{device_number}. {multiplexer}. Channel {channel_number:02d} & {channel_number + 10:02d}" if device_number else ""

        resistor_data = {
            'board_num': board_num,
            'resistor_num': resistor_num,
            'selected_device': tk.StringVar(value=selected_device_str),
            'pt_enabled': tk.BooleanVar(value=pt_enabled),
            'selected_pt': tk.StringVar(value=pt_value),
            'dropdown': None  # Dies wird später zugewiesen
        }
        boards_dict[board_num]['resistors'].append(resistor_data)

    for board_num in sorted(boards_dict.keys()):
        preboard_config.append(boards_dict[board_num])

    return preboard_config

def print_preboard_config(preboard_config):
    for board in preboard_config:
        debug_print(f"Board {board['resistors'][0]['board_num']} ----")
        for resistor in board['resistors']:
            board_num = resistor['board_num']
            resistor_num = resistor['resistor_num']
            selected_device = resistor['selected_device'].get()
            pt_enabled = resistor['pt_enabled'].get()
            selected_pt = resistor['selected_pt'].get() if pt_enabled else "False"
            debug_print(f"    {board_num}, {resistor_num}, {selected_device}, {pt_enabled}, {selected_pt}")
