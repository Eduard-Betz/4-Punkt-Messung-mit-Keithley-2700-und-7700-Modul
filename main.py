#Main.py

import serial
import serial.tools.list_ports

from global_vars import gefundenen_geraete

from MainGUI import MainApp

from Tab1.finder import Finder



Baudrate = 9600

def finder_callback():
    finder = Finder(Baudrate)
    ports = [port.device for port in serial.tools.list_ports.comports()]
    neue_geraete = []

    for port in ports:
        idn, mod1, mod2 = finder.find_device(port)
        if idn:
            neue_geraete.append((port, idn, mod1, mod2))

    if not neue_geraete:
        neue_geraete.append(["NaN", "NaN", "NaN", "NaN"])

    gefundenen_geraete.update_geraete(neue_geraete)
    ausgabe_gefundenen_geraete(gefundenen_geraete.geraete)

# Funktion zur Ausgabe der gefundenen Geräte
def ausgabe_gefundenen_geraete(geraete):
    if not geraete or (len(geraete) == 1 and geraete[0] == ["NaN", "NaN", "NaN", "NaN"]):
        print("Keine Geräte gefunden.")
    else:
        for port, idn, mod1, mod2 in geraete:
            print(f"Port: {port}, IDN: {idn}, Modul in Port 1: {mod1}, Modul in Port 2: {mod2}")

def variable_changed(var_name, *args):
    print(f"{var_name}: {globals()[var_name].get()}")

def main():
    app = MainApp(finder_callback)
    app.mainloop()

if __name__ == "__main__":
    main()
