# MainGui.py

import tkinter as tk
from tkinter import ttk
from Tab1.tab1 import create_tab1
from Tab2.tab2 import create_tab2
from Tab3.tab3 import create_tab3
from Tab4.tab4 import create_tab4
from resize_handler import on_resize
from Tab3.Messungen import stop_measurement
import threading  # Importiere threading, um stop_event zu erstellen

class MainApp(tk.Tk):
    def __init__(self, finder_callback):
        super().__init__()
        self.title("Main GUI")
        self.geometry("1600x900")

        self.finder_callback = finder_callback
        self.stop_event = threading.Event()  # Initialisiere stop_event

        self.create_style()

        self.notebook = ttk.Notebook(self, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)

        self.create_tabs()

        # Binde das <Configure> Event, um die Größe der Tab-Schriftarten anzupassen
        self.bind("<Configure>", self.on_resize_wrapper)

        # Sicherstellen, dass das Programm ordnungsgemäß beendet wird
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        print("Programm wird geschlossen...")
        # Hier wird sichergestellt, dass der Thread sauber beendet wird, falls eine Messung läuft
        stop_measurement(self.stop_event)  # Übergib stop_event an stop_measurement
        self.destroy()
        print("Programm geschlossen.")

    def create_style(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.TNotebook.Tab', padding=[55, 20])
        style.configure('Custom.TNotebook', tabposition='sw')  # Tabs unten positionieren

        # Stil für das Aussehen der Tabs anpassen, um die obere Kante zu entfernen
        style.map("Custom.TNotebook.Tab",
            expand=[("selected", [1, 1, 1, 0])]  # Entferne die obere Kante des ausgewählten Tabs
        )
        
        style.layout('Custom.TNotebook.Tab', [
            ('Notebook.tab', {
                'children': [
                    ('Notebook.padding', {
                        'children': [
                            ('Notebook.focus', {
                                'children': [
                                    ('Notebook.label', {'side': 'top', 'sticky': 'nswe'})
                                ]
                            })
                        ],
                        'side': 'top', 'sticky': 'nswe'
                    })
                ],
                'side': 'top', 'sticky': 'nswe'
            })
        ])

    def create_tabs(self):
        create_tab1(self.notebook, self.finder_callback)
        create_tab2(self.notebook)
        create_tab3(self.notebook, self.switch_to_tab4)  # Übergib die Tab-Wechsel-Funktion
        create_tab4(self.notebook)

    def switch_to_tab4(self):
        """Wechselt zu Tab 4."""
        self.notebook.select(3)  # Tab 4 auswählen (Tab-Indizes beginnen bei 0)

    def on_resize_wrapper(self, event):
        elements = []
        for tab in self.notebook.winfo_children():
            elements.extend(tab.winfo_children())
        on_resize(event, self.notebook, elements)
