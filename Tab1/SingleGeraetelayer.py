# SingleGeraetelayer.py
import tkinter as tk
from tkinter import ttk
from global_vars import Geraet  # Importiere die globale Geräteverwaltung

# Definiere das Debug-Flag und die debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class SingleGeraetelayer(ttk.LabelFrame):
    def __init__(self, parent, devices, initial_port, device_number, device_data):
        self.device_number = device_number
        self.devices = [list(device) for device in devices]  # Umwandlung in Liste
        self.initial_port = initial_port
        self.device_data = list(device_data)  # Umwandlung in eine Liste, falls es ein Tupel ist

        debug_print(f"Initialisiere SingleGeraetelayer mit: devices={devices}, initial_port={initial_port}, device_number={device_number}, device_data={device_data}")

        device_name = self.get_device_name(initial_port)
        super().__init__(parent, text=f"{device_number}, {device_name}")

        self.create_widgets()
        self.update_title(initial_port)

    def create_widgets(self):
        # Combobox für Ports
        self.port_var = tk.StringVar(value=self.initial_port)
        ports = [device[0] for device in self.devices]
        self.port_combobox = ttk.Combobox(self, textvariable=self.port_var, values=ports)
        self.port_combobox.bind("<<ComboboxSelected>>", self.on_combobox_change)
        self.port_combobox.bind("<FocusOut>", self.on_combobox_change)  # Hinzufügen des Event-Handlers für manuelle Eingaben
        self.port_combobox.bind("<Return>", self.on_combobox_change)    # Aktualisierung bei Drücken der Enter-Taste
        self.port_combobox.grid(row=0, column=0, padx=10, pady=2, sticky="ew")

        # Anzeige für Modul 1 und Modul 2
        self.module_frame_1 = self.create_module_display()
        self.module_frame_1.grid(row=1, column=0, padx=10, pady=2, sticky="ew")

        self.module_frame_2 = self.create_module_display()
        self.module_frame_2.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

    def create_module_display(self):
        frame = ttk.Frame(self)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        canvas = tk.Canvas(frame, width=20, height=20)
        canvas.grid(row=0, column=0, padx=5)
        canvas.create_oval(5, 5, 15, 15, fill="red")

        module_label = ttk.Label(frame, text="", anchor='center', width=20)
        module_label.grid(row=0, column=1, padx=5)

        frame.canvas = canvas
        frame.module_label = module_label

        return frame

    def update_title(self, new_port):
        device_name = self.get_device_name(new_port)
        self.config(text=f"{self.device_number}, {device_name}")
        for device in self.devices:
            if device[0] == new_port:
                self.update_module_display(device[2], device[3])
                break

    def update_module_display(self, module1, module2):
        self.set_module_display(self.module_frame_1, module1)
        self.set_module_display(self.module_frame_2, module2)

    def set_module_display(self, frame, module):
        color = "red" if module == "NaN" else "green"
        frame.canvas.delete("all")
        frame.canvas.create_oval(5, 5, 15, 15, fill=color)
        frame.module_label.config(text=module)

    def get_device_name(self, port):
        for device in self.devices:
            if device[0] == port:
                return device[1]
        return ""

    def update_device_data(self, new_port):
        device_name = self.get_device_name(new_port)
        self.device_data = list(self.device_data)  # Sicherstellen, dass es eine Liste ist
        self.device_data[1] = new_port
        self.device_data[2] = device_name
        self.device_data[3] = (self.module_frame_1.module_label.cget("text"), self.module_frame_2.module_label.cget("text"))
        self.update_title(new_port)
        self.update_global_device_data(new_port)

    def update_global_device_data(self, new_port):
        for device in self.devices:
            if device[0] == new_port:
                device[2] = self.module_frame_1.module_label.cget("text")
                device[3] = self.module_frame_2.module_label.cget("text")
                break
        Geraet.update_geraet(self.device_number, new_port, self.module_frame_1.module_label.cget("text"), self.module_frame_2.module_label.cget("text"))

    def on_combobox_change(self, event=None):
        new_port = self.port_var.get()
        self.update_device_data(new_port)
