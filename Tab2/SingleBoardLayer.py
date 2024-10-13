#SingleBaordLayer.py

import tkinter as tk
from tkinter import ttk

from global_vars import BoardConfig

from Tab2.ConfigTranslator import translate_preboard_to_boardconfig, print_preboard_config

# Definieren des Debug-Flags und der debug_print-Funktion
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def create_board_frame(parent, board_num, devices, resistors_per_board, preboard_resistors=None):
    frame = tk.LabelFrame(parent, text=f"Board {board_num}")

    resistors = []
    for resistor_num in range(1, resistors_per_board + 1):
        resistor_frame = tk.Frame(frame)
        resistor_frame.grid(row=resistor_num - 1, column=0, pady=5, sticky="ew")

        label = tk.Label(resistor_frame, text=f"{resistor_num}")
        label.pack(side=tk.LEFT, padx=5)

        device_options = []
        for device in devices:
            device_number = device['device_number']
            if device['multiplexer1']:
                for ch in range(1, 11):
                    device_options.append(f"{device_number}. 1. Channel {ch:02d} & {ch + 10:02d}")
            if device['multiplexer2']:
                for ch in range(1, 11):
                    device_options.append(f"{device_number}. 2. Channel {ch:02d} & {ch + 10:02d}")

        selected_device = tk.StringVar()
        dropdown = ttk.Combobox(resistor_frame, textvariable=selected_device, values=device_options)
        dropdown.pack(side=tk.LEFT, padx=5)

        pt_enabled = tk.BooleanVar()
        pt_check = tk.Checkbutton(resistor_frame, text="PT", variable=pt_enabled)
        pt_check.pack(side=tk.LEFT, padx=5)

        pt_options = ["", "PT100", "PT500", "PT1000"]
        selected_pt = tk.StringVar()
        pt_dropdown = ttk.Combobox(resistor_frame, textvariable=selected_pt, values=pt_options, state='disabled', width=10)
        pt_dropdown.pack(side=tk.LEFT, padx=5)

        if preboard_resistors:
            # Setze die gespeicherten Werte
            for resistor in preboard_resistors:
                if resistor['resistor_num'] == resistor_num:
                    selected_device.set(resistor['selected_device'].get())
                    pt_enabled.set(resistor['pt_enabled'].get())
                    selected_pt.set(resistor['selected_pt'].get())
                    if pt_enabled.get():
                        pt_dropdown['state'] = 'normal'
                    else:
                        pt_dropdown.set("")
                        pt_dropdown['state'] = 'disabled'

        def create_on_pt_check_change(pt_enabled, pt_dropdown):
            def on_pt_check_change():
                if pt_enabled.get():
                    pt_dropdown['state'] = 'normal'
                else:
                    pt_dropdown.set("")
                    pt_dropdown['state'] = 'disabled'
                on_config_change()
            return on_pt_check_change

        pt_check.config(command=create_on_pt_check_change(pt_enabled, pt_dropdown))

        selected_device.trace('w', lambda name, index, mode, var=selected_device: on_config_change())
        selected_pt.trace('w', lambda name, index, mode, var=selected_pt: on_config_change())
        pt_enabled.trace('w', lambda name, index, mode, var=pt_enabled: on_config_change())

        resistor_data = {
            'board_num': board_num,
            'resistor_num': resistor_num,
            'selected_device': selected_device,
            'pt_enabled': pt_enabled,
            'selected_pt': selected_pt,
            'dropdown': dropdown
        }
        resistors.append(resistor_data)

    return {'frame': frame, 'resistors': resistors}

def on_config_change(*args):
    from Tab2.TabBoards import PreBoardConfig
    board_config = translate_preboard_to_boardconfig(PreBoardConfig)
    BoardConfig.update_board_config(board_config)
    debug_print("Konfiguration geändert:")
    for config in board_config:
        debug_print(config)
    debug_print("Aktuelle PreBoardConfig:")
    print_preboard_config(PreBoardConfig)
