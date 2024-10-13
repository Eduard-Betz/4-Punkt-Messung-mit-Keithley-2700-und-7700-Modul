# global_vars.py
DEBUG = False

def debug_Gloabel_Vars_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class GefundenenGeraete:
    def __init__(self):
        self.geraete = [["NaN", "NaN", "NaN", "NaN"]]
        self.callbacks = []
        self.variables = {
            'baudrate': '9600',
            'anzahl': '0',
            'boards': '0',
            'widerstaende': '0'
        }

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def notify_callbacks(self):
        for callback in self.callbacks:
            callback()

    def update_geraete(self, new_geraete):
        self.geraete = new_geraete
        self.notify_callbacks()

    def update_variable(self, var_name, value):
        if var_name in self.variables:
            self.variables[var_name] = value
            self.notify_callbacks()

    def get_variable(self, var_name):
        return self.variables.get(var_name, '')

gefundenen_geraete = GefundenenGeraete()

class GeraeteManager:
    def __init__(self):
        self.geraete = []
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def notify_callbacks(self):
        for callback in self.callbacks:
            callback()

    def update_geraet(self, geraet_nummer, port, mod1, mod2):
        for idx, geraet in enumerate(self.geraete):
            if geraet[0] == geraet_nummer:
                self.geraete[idx] = (geraet_nummer, port, mod1, mod2)
                self.notify_callbacks()
                return
        self.geraete.append((geraet_nummer, port, mod1, mod2))
        self.notify_callbacks()

    def get_geraet(self, geraet_nummer):
        for geraet in self.geraete:
            if geraet[0] == geraet_nummer:
                return geraet
        return None

Geraet = GeraeteManager()


class BoardConfigManager:
    def __init__(self):
        self.board_config = []

    def update_board_config(self, new_config):
        self.board_config = new_config

    def get_board_config(self):
        return self.board_config

BoardConfig = BoardConfigManager()

Messwerte = []

Zeitverzögertemessung = False
Zeitverzögerungswert = "2:00"

# Neue globale Variablen für die Auswahl der Plots
class PlotAuswahlManager:
    def __init__(self):
        self.steigung = None
        self.sinkend = None

    def get_steigung(self):
        return self.steigung

    def get_sinkend(self):
        return self.sinkend

    def set_steigung(self, steigung):
        self.steigung = steigung

    def set_sinkend(self, sinkend):
        self.sinkend = sinkend

    # Neue Methoden zum Aktualisieren der Steigungs- und Sinkendaten
    def update_steigung(self, steigung):
        self.steigung = steigung

    def update_sinkend(self, sinkend):
        self.sinkend = sinkend

    # Methoden zum Zurücksetzen
    def reset_steigung(self):
        self.steigung = None

    def reset_sinkend(self):
        self.sinkend = None

# Initialisiere den PlotAuswahlManager
PlotAuswahl = PlotAuswahlManager()



class PlotwerteManager:
    def __init__(self):
        self.plotwerte = {}  # Hier werden die Plotwerte für Boards und Widerstände gespeichert
        self.letzte_werte = {}  # Hier werden die letzten gültigen Werte für Boards und Widerstände gespeichert

    def get_plotwerte(self):
        return self.plotwerte

    def clear_plotwerte(self):
        """
        Leert die PlotWerte.
        """
        self.plotwerte.clear()

    def filtere_wert(self, board_nr, widerstand_nr, temperatur_true, neuer_wert):
        # Initialisiere die letzte_werte Struktur für das Board und den Widerstand
        if board_nr not in self.letzte_werte:
            self.letzte_werte[board_nr] = {}
        if widerstand_nr not in self.letzte_werte[board_nr]:
            self.letzte_werte[board_nr][widerstand_nr] = None

        # Setze den neuen Wert, unabhängig von der Abweichung oder vorherigen Werten
        self.letzte_werte[board_nr][widerstand_nr] = neuer_wert
        return neuer_wert

    def umwandeln_in_plotwerte(self, messwerte):
        """
        Wandelt die aktuellen Messwerte in Plotwerte um und speichert diese.
        """
        self.clear_plotwerte()
        for messung in messwerte:
            zeit = messung[0]
            board_nr = messung[1]
            widerstand_nr = messung[2]
            temperatur_true = messung[5]
            widerstand = messung[7]
            temperatur = messung[8]

            # Wähle den richtigen Wert (Temperatur oder Widerstand) basierend auf `temperatur_true`
            wert = temperatur if temperatur_true else widerstand

            # Führe den Wert durch den Filter
            gefilterter_wert = self.filtere_wert(board_nr, widerstand_nr, temperatur_true, wert)

            if gefilterter_wert is None:
                continue

            if board_nr not in self.plotwerte:
                self.plotwerte[board_nr] = (True, {})

            if widerstand_nr not in self.plotwerte[board_nr][1]:
                self.plotwerte[board_nr][1][widerstand_nr] = (temperatur_true, {"time": [], "values": []})

            self.plotwerte[board_nr][1][widerstand_nr][1]["time"].append(zeit)
            self.plotwerte[board_nr][1][widerstand_nr][1]["values"].append(gefilterter_wert)

# Initialisiere den PlotwerteManager
Plotwerte = PlotwerteManager()



class TKBoardVariabelnManager:
    def __init__(self):
        self.board_variablen = {}

    # Normale Temperaturen speichern
    def update_board(self, board_nr, resistor_nr, steigung_steigend, temp_bereich_steigend, steigung_sinkend, temp_bereich_sinkend, temp_min, temp_max):
        board_nr = str(board_nr).replace('Board ', '')
        if board_nr not in self.board_variablen:
            self.board_variablen[board_nr] = {}
        if resistor_nr not in self.board_variablen[board_nr]:
            self.board_variablen[board_nr][resistor_nr] = {}
        self.board_variablen[board_nr][resistor_nr]['normal'] = {
            'steigung_steigend': steigung_steigend,
            'temp_bereich_steigend': temp_bereich_steigend,
            'steigung_sinkend': steigung_sinkend,
            'temp_bereich_sinkend': temp_bereich_sinkend,
            'temp_min': temp_min,
            'temp_max': temp_max
        }

    # Gemittelte Temperaturen speichern
    def update_board_avg(cls, board_nr, resistor_nr, steigung_steigend, temp_bereich_steigend, steigung_sinkend, temp_bereich_sinkend):
        if board_nr not in cls.board_variablen:
            cls.board_variablen[board_nr] = {}
        if resistor_nr not in cls.board_variablen[board_nr]:
            cls.board_variablen[board_nr][resistor_nr] = {}
        cls.board_variablen[board_nr][resistor_nr]['avg'] = {
            'steigung_steigend': steigung_steigend,
            'temp_bereich_steigend': temp_bereich_steigend,
            'steigung_sinkend': steigung_sinkend,
            'temp_bereich_sinkend': temp_bereich_sinkend
        }

    def get_board_data(self, board_nr):
        return self.board_variablen.get(board_nr, None)

    def clear(self):
        self.board_variablen.clear()


# Initialisiere TKBoardVariabeln
TKBoardVariabeln = TKBoardVariabelnManager()

