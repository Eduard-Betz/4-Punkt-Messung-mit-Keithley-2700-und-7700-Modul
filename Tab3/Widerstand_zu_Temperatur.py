# Widerstand_zu_Temperatur.py

#debugging_WiderstandZuTemperatur-Variable
debugging_WiderstandZuTemperatur = False

def debug_print(message):
    if debugging_WiderstandZuTemperatur:
        print(message)

def resistance_to_temperature(resistance, sensor_type):
    # Konstanten für PT-Sensoren
    A = 3.9083e-3
    B = -5.775e-7

    # Debugging: Ausgabe der Eingangswerte
    debug_print(f"DEBUG: Berechnung für Widerstand: {resistance}, Sensortyp: {sensor_type}")

    if sensor_type == 'PT100':
        R0 = 100.0
    elif sensor_type == 'PT500':
        R0 = 500.0
    elif sensor_type == 'PT1000':
        R0 = 1000.0
    else:
        raise ValueError(f"Unbekannter Sensortyp: {sensor_type}")

    # Berechnung der Temperatur
    if resistance >= R0:
        # Positive Temperaturen
        temp = (-A + (A**2 - 4*B*(1 - resistance/R0))**0.5) / (2*B)
    else:
        # Negative Temperaturen (vereinfachte Näherung)
        temp = (resistance / R0 - 1) / A

    # Debugging: Ausgabe des berechneten Temperaturwertes
    debug_print(f"DEBUG: Berechnete Temperatur: {temp:.2f} °C")

    return temp

