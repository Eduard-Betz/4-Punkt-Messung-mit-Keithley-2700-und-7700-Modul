#BoardConfigSaveNLoad.py

import json
from global_vars import gefundenen_geraete, Geraet, BoardConfig

# Definiere das Debug-Flag und die debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def save_config(file_path):
    data = {
        "Baudrate": gefundenen_geraete.get_variable('baudrate'),
        "Anzahl_der_geraete": gefundenen_geraete.get_variable('anzahl'),
        "Anzahl_der_Boards": gefundenen_geraete.get_variable('boards'),
        "Widerstaende_pro_Board": gefundenen_geraete.get_variable('widerstaende'),
        "Gefundene_Geraete": gefundenen_geraete.geraete,
        "Geraete_Konfiguration": Geraet.geraete,
        "Board_Config": BoardConfig.get_board_config()
    }

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    debug_print(f"Konfiguration erfolgreich in {file_path} gespeichert.")

def load_config(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    gefundenen_geraete.update_variable('baudrate', data["Baudrate"])
    gefundenen_geraete.update_variable('anzahl', data["Anzahl_der_geraete"])
    gefundenen_geraete.update_variable('boards', data["Anzahl_der_Boards"])
    gefundenen_geraete.update_variable('widerstaende', data["Widerstaende_pro_Board"])
    gefundenen_geraete.update_geraete(data["Gefundene_Geraete"])

    Geraet.geraete = data["Geraete_Konfiguration"]
    Geraet.notify_callbacks()

    BoardConfig.update_board_config(data["Board_Config"])

    debug_print(f"Konfiguration erfolgreich aus {file_path} geladen.")

def print_config():
    debug_print("Aktuelle Konfiguration:")
    debug_print(f"Baudrate: {gefundenen_geraete.get_variable('baudrate')}")
    debug_print(f"Anzahl der Geräte: {gefundenen_geraete.get_variable('anzahl')}")
    debug_print(f"Anzahl der Boards: {gefundenen_geraete.get_variable('boards')}")
    debug_print(f"Widerstände pro Board: {gefundenen_geraete.get_variable('widerstaende')}")
    debug_print("Gefundene Geräte:")
    for device in gefundenen_geraete.geraete:
        debug_print(device)
    debug_print("Gerätekonfiguration:")
    for config in Geraet.geraete:
        debug_print(config)
    debug_print("Board Config:")
    for board in BoardConfig.get_board_config():
        debug_print(board)
