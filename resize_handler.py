# resize_handler.py
import tkinter as tk
from tkinter import ttk

def on_resize(event, widget, elements):
    width, height = event.width, event.height

    # Schriftgröße anpassen
    font_size = max(8, int(height / 30))
    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", font_size))
    style.configure("TEntry", font=("Helvetica", font_size))
    style.configure("TCombobox", font=("Helvetica", font_size))
    style.configure("TButton", font=("Helvetica", font_size))
    style.configure("TLabelFrame", font=("Helvetica", font_size))
    style.configure("Custom.TNotebook.Tab", font=("Helvetica", font_size))

    # Font-Objekt für Eingabefelder, Combobox und Buttons
    entry_font = ('Helvetica', font_size)

    # Liste der Widgets, die die font-Option unterstützen
    font_supported_widgets = (ttk.Combobox, ttk.Entry, tk.Button, ttk.Label, ttk.LabelFrame, tk.OptionMenu)

    # Elemente iterieren und anpassen
    for element in elements:
        if isinstance(element, font_supported_widgets):
            try:
                element.config(font=entry_font)
            except tk.TclError:
                pass

        if isinstance(element, ttk.Combobox):
            element.pack_configure(ipady=font_size // 4, padx=font_size // 4)
        elif isinstance(element, ttk.Entry):
            element.pack_configure(ipady=font_size // 4, padx=font_size // 4)
        elif isinstance(element, ttk.LabelFrame):
            for child in element.winfo_children():
                if isinstance(child, font_supported_widgets):
                    try:
                        child.config(font=entry_font)
                    except tk.TclError:
                        pass
                if isinstance(child, ttk.Combobox):
                    child.pack_configure(ipady=font_size // 4, padx=font_size // 4)
                elif isinstance(child, ttk.Entry):
                    child.pack_configure(ipady=font_size // 4, padx=font_size // 4)
        elif isinstance(element, tk.OptionMenu):
            menu = element["menu"]
            try:
                menu.config(font=entry_font)
                element.config(font=entry_font)
                element.config(height=font_size // 16, width=width // 30)  # Höhe und Breite des OptionMenu anpassen
            except tk.TclError:
                pass
        elif isinstance(element, tk.Button):
            try:
                element.config(font=entry_font)
            except tk.TclError:
                pass
