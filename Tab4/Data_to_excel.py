# Datei: Data_to_excel.py

from global_vars import TKBoardVariabeln, TK_Fehler, PlotAuswahl  # TK_Fehler importieren

import pandas as pd
from tkinter import filedialog



# Debug-Flag definieren
debug_Tab4 = False  # Debug-Ausgaben sind standardmäßig deaktiviert

# Debug-Ausgabefunktion
def debug_print(*args, **kwargs):
    if debug_Tab4:
        print(*args, **kwargs)

def print_tk_data():
    # Öffne einen Dialog, um den Speicherort der Excel-Datei zu wählen
    file_path = filedialog.asksaveasfilename(
        defaultextension='.xlsx',
        filetypes=[('Excel Dateien', '*.xlsx'), ('Alle Dateien', '*.*')],
        title='Excel-Datei speichern'
    )

    if not file_path:
        # Benutzer hat den Dialog abgebrochen
        return

    data = TKBoardVariabeln.board_variablen

    # Debug-Ausgabe hinzufügen
    debug_print("Inhalt von TKBoardVariabeln.board_variablen:")
    debug_print(data)

    # Listen zur Speicherung der Daten für die Tabellen
    normal_data_list = []
    avg_data_list = []

    # Daten extrahieren
    for board_nr, resistors in data.items():
        for resistor_nr, values in resistors.items():
            # Gemeinsame Daten
            row_common = {
                'Board Nr.': board_nr,
                'Probe': '',  # Diese Spalte bleibt leer
            }

            # R²-Werte und delta_alpha_total aus TK_Fehler holen
            fehler_data = TK_Fehler.get_board_data(board_nr)
            resistor_fehler = fehler_data.get(resistor_nr, {}) if fehler_data else {}

            # Normal Daten
            if 'normal' in values:
                normal = values['normal']
                # Runden der Temperaturwerte auf zwei Dezimalstellen
                temp_steigend = normal.get('temp_bereich_steigend', (None, None))
                temp_fallend = normal.get('temp_bereich_sinkend', (None, None))

                temp_steigend = tuple(round(t, 2) if isinstance(t, (int, float)) else t for t in temp_steigend)
                temp_fallend = tuple(round(t, 2) if isinstance(t, (int, float)) else t for t in temp_fallend)

                # Fehlerdaten für normale Daten
                normal_fehler = resistor_fehler.get('normal', {})
                r_squared_steigend = normal_fehler.get('r_squared_steigend', '')
                r_squared_fallend = normal_fehler.get('r_squared_sinkend', '')
                delta_alpha_total_steigend = normal_fehler.get('delta_alpha_total_steigend', '')
                delta_alpha_total_fallend = normal_fehler.get('delta_alpha_total_sinkend', '')

                normal_row = row_common.copy()
                normal_row.update({
                    'TK_steigende': normal.get('steigung_steigend', ''),
                    'Fehler ±_steigende': delta_alpha_total_steigend,  # ∆αGesamt hinzufügen
                    'R²_steigende': r_squared_steigend,  # R²-Wert hinzufügen
                    'min temp_steigende': temp_steigend[0],
                    'max temp_steigende': temp_steigend[1],

                    'TK_fallende': normal.get('steigung_sinkend', ''),
                    'Fehler ±_fallende': delta_alpha_total_fallend,  # ∆αGesamt hinzufügen
                    'R²_fallende': r_squared_fallend,     # R²-Wert hinzufügen
                    'min temp_fallende': temp_fallend[0],
                    'max temp_fallende': temp_fallend[1],
                })
                normal_data_list.append(normal_row)

            # Avg Daten
            if 'avg' in values:
                avg = values['avg']
                # Runden der Temperaturwerte auf zwei Dezimalstellen
                temp_steigend = avg.get('temp_bereich_steigend', (None, None))
                temp_fallend = avg.get('temp_bereich_sinkend', (None, None))

                temp_steigend = tuple(round(t, 2) if isinstance(t, (int, float)) else t for t in temp_steigend)
                temp_fallend = tuple(round(t, 2) if isinstance(t, (int, float)) else t for t in temp_fallend)

                # Fehlerdaten für avg Daten
                avg_fehler = resistor_fehler.get('avg', {})
                r_squared_steigend_avg = avg_fehler.get('r_squared_steigend', '')
                r_squared_fallend_avg = avg_fehler.get('r_squared_sinkend', '')
                delta_alpha_total_steigend_avg = avg_fehler.get('delta_alpha_total_steigend', '')
                delta_alpha_total_fallend_avg = avg_fehler.get('delta_alpha_total_sinkend', '')

                avg_row = row_common.copy()
                avg_row.update({
                    'TK_steigende': avg.get('steigung_steigend', ''),
                    'Fehler ±_steigende': delta_alpha_total_steigend_avg,  # ∆αGesamt hinzufügen
                    'R²_steigende': r_squared_steigend_avg,  # R²-Wert hinzufügen
                    'min temp_steigende': temp_steigend[0],
                    'max temp_steigende': temp_steigend[1],

                    'TK_fallende': avg.get('steigung_sinkend', ''),
                    'Fehler ±_fallende': delta_alpha_total_fallend_avg,  # ∆αGesamt hinzufügen
                    'R²_fallende': r_squared_fallend_avg,     # R²-Wert hinzufügen
                    'min temp_fallende': temp_fallend[0],
                    'max temp_fallende': temp_fallend[1],
                })
                avg_data_list.append(avg_row)

    # Überprüfen, ob Daten in den Listen vorhanden sind
    if not normal_data_list and not avg_data_list:
        debug_print("Keine Daten zum Exportieren gefunden.")
        return

    # Spalten definieren
    columns = [
        'Board Nr.', 'Probe',
        'TK_steigende', 'Fehler ±_steigende', 'R²_steigende', 'min temp_steigende', 'max temp_steigende',
        'TK_fallende', 'Fehler ±_fallende', 'R²_fallende', 'min temp_fallende', 'max temp_fallende'
    ]

    normal_df = pd.DataFrame(normal_data_list, columns=columns)
    avg_df = pd.DataFrame(avg_data_list, columns=columns)

    # Daten in Excel schreiben mit xlsxwriter
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Erstes Tabellenblatt erstellen
        sheet_name = 'TK_Data'
        worksheet = workbook.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = worksheet

        # Formate definieren
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
        group_header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 2})
        column_header_format = workbook.add_format({'bold': True, 'align': 'center', 'bottom': 1})
        cell_format = workbook.add_format({'align': 'center'})

        # Überschrift für normale Daten schreiben
        normal_header_row_excel = 0
        normal_header = "TK mit Board Temperatur"
        worksheet.merge_range(normal_header_row_excel, 0, normal_header_row_excel, len(columns)-1, normal_header, header_format)

        # Gruppenkopfzeilen hinzufügen
        group_header_row = 1  # Zeile für Gruppenkopfzeilen
        column_header_row = 2  # Zeile für Spaltenüberschriften

        # "Steigende Flanke" über Spalten 2 bis 6
        worksheet.merge_range(group_header_row, 2, group_header_row, 6, 'Steigende Flanke', group_header_format)

        # "Fallende Flanke" über Spalten 7 bis 11
        worksheet.merge_range(group_header_row, 7, group_header_row, 11, 'Fallende Flanke', group_header_format)

        # Suffixe aus Spaltenüberschriften entfernen und formatieren
        for col_num, value in enumerate(columns):
            header_text = value.replace('_steigende', '').replace('_fallende', '').replace('∆αGesamt', 'Fehler ±')
            worksheet.write(column_header_row, col_num, header_text, column_header_format)
            # Wenden Sie das Zellenformat auf die gesamte Spalte an
            worksheet.set_column(col_num, col_num, 20, cell_format)

        # Daten manuell schreiben und Rahmen anwenden
        normal_table_start_row = 3
        data_values = normal_df.values.tolist()
        num_rows = len(data_values)
        num_cols = len(columns)
        for row_idx, row_data in enumerate(data_values):
            excel_row = normal_table_start_row + row_idx
            for col_idx, cell_value in enumerate(row_data):
                excel_col = col_idx

                # Standardformat
                fmt_dict = {'align': 'center'}

                # Rahmen für Steigende Flanke
                if 2 <= excel_col <= 6:
                    # Zelle an der oberen Grenze
                    if excel_row == normal_table_start_row:
                        fmt_dict['top'] = 2
                    # Zelle an der unteren Grenze
                    if excel_row == normal_table_start_row + num_rows - 1:
                        fmt_dict['bottom'] = 2
                    # Zelle an der linken Grenze
                    if excel_col == 2:
                        fmt_dict['left'] = 2
                    # Zelle an der rechten Grenze
                    if excel_col == 6:
                        fmt_dict['right'] = 2

                # Rahmen für Fallende Flanke
                if 7 <= excel_col <= 11:
                    # Zelle an der oberen Grenze
                    if excel_row == normal_table_start_row:
                        fmt_dict['top'] = 2
                    # Zelle an der unteren Grenze
                    if excel_row == normal_table_start_row + num_rows - 1:
                        fmt_dict['bottom'] = 2
                    # Zelle an der linken Grenze
                    if excel_col == 7:
                        fmt_dict['left'] = 2
                    # Zelle an der rechten Grenze
                    if excel_col == 11:
                        fmt_dict['right'] = 2

                # Format erstellen
                fmt = workbook.add_format(fmt_dict)

                # Zelle schreiben
                worksheet.write(excel_row, excel_col, cell_value, fmt)

        # Schreibe avg_df unter normal_df mit etwas Abstand
        avg_header_row = normal_table_start_row + num_rows + 2
        avg_header = "TK mit gemittelter Temperatur über alle Boards"
        worksheet.merge_range(avg_header_row, 0, avg_header_row, len(columns)-1, avg_header, header_format)

        # Gruppenkopfzeilen für avg-Daten hinzufügen
        group_header_row_avg = avg_header_row + 1
        column_header_row_avg = avg_header_row + 2

        worksheet.merge_range(group_header_row_avg, 2, group_header_row_avg, 6, 'Steigende Flanke', group_header_format)
        worksheet.merge_range(group_header_row_avg, 7, group_header_row_avg, 11, 'Fallende Flanke', group_header_format)

        # Suffixe aus Spaltenüberschriften entfernen und formatieren
        for col_num, value in enumerate(columns):
            header_text = value.replace('_steigende', '').replace('_fallende', '').replace('∆αGesamt', 'Fehler ±')
            worksheet.write(column_header_row_avg, col_num, header_text, column_header_format)
            # Wenden Sie das Zellenformat auf die gesamte Spalte an
            worksheet.set_column(col_num, col_num, 20, cell_format)

        # Daten manuell schreiben und Rahmen anwenden
        avg_table_start_row = column_header_row_avg + 1
        data_values = avg_df.values.tolist()
        num_rows_avg = len(data_values)
        for row_idx, row_data in enumerate(data_values):
            excel_row = avg_table_start_row + row_idx
            for col_idx, cell_value in enumerate(row_data):
                excel_col = col_idx

                # Standardformat
                fmt_dict = {'align': 'center'}

                # Rahmen für Steigende Flanke
                if 2 <= excel_col <= 6:
                    # Zelle an der oberen Grenze
                    if excel_row == avg_table_start_row:
                        fmt_dict['top'] = 2
                    # Zelle an der unteren Grenze
                    if excel_row == avg_table_start_row + num_rows_avg - 1:
                        fmt_dict['bottom'] = 2
                    # Zelle an der linken Grenze
                    if excel_col == 2:
                        fmt_dict['left'] = 2
                    # Zelle an der rechten Grenze
                    if excel_col == 6:
                        fmt_dict['right'] = 2

                # Rahmen für Fallende Flanke
                if 7 <= excel_col <= 11:
                    # Zelle an der oberen Grenze
                    if excel_row == avg_table_start_row:
                        fmt_dict['top'] = 2
                    # Zelle an der unteren Grenze
                    if excel_row == avg_table_start_row + num_rows_avg - 1:
                        fmt_dict['bottom'] = 2
                    # Zelle an der linken Grenze
                    if excel_col == 7:
                        fmt_dict['left'] = 2
                    # Zelle an der rechten Grenze
                    if excel_col == 11:
                        fmt_dict['right'] = 2

                # Format erstellen
                fmt = workbook.add_format(fmt_dict)

                # Zelle schreiben
                worksheet.write(excel_row, excel_col, cell_value, fmt)

        # Nun integrieren wir die Funktionalität von TK_auswahl_zu_excel()

        # Überprüfen, ob PlotAuswahl definiert ist
        try:
            if PlotAuswahl is None:
                print("Die Variable PlotAuswahl ist nicht definiert.")
                return
        except NameError:
            print("Die Variable PlotAuswahl ist nicht definiert.")
            return

        # Liste der Datensätze und zugehörigen Sheetnamen
        datasets = []
        if hasattr(PlotAuswahl, 'steigung') and PlotAuswahl.steigung is not None:
            datasets.append(('steigende Flanke', PlotAuswahl.steigung))
        if hasattr(PlotAuswahl, 'sinkend') and PlotAuswahl.sinkend is not None:
            datasets.append(('fallende Flanke', PlotAuswahl.sinkend))

        if not datasets:
            print("Keine gültigen Daten in PlotAuswahl gefunden.")
            return

        for sheet_name_plot, plot_data in datasets:
            status, boards_data = plot_data

            # Neues Blatt erstellen
            worksheet = workbook.add_worksheet(sheet_name_plot)
            writer.sheets[sheet_name_plot] = worksheet

            # Ermitteln der maximalen Anzahl von Messpunkten
            max_messpunkte = max(len(data[1]) for data in boards_data.values())

            # Initialisiere die Spalten
            spalten = ['Messpunkt']

            # Erstelle ein Dictionary, das die Anzahl der Widerstände pro Board speichert
            widerstand_counts = {}

            # Boards sortieren für konsistente Spaltenreihenfolge
            sorted_boards = sorted(boards_data.keys())

            for board_name in sorted_boards:
                board_status, datenpunkte = boards_data[board_name]
                # Anzahl der Widerstände ermitteln (Annahme: Temperatur ist der letzte Wert, Zeitpunkt ist der erste)
                beispiel_datenpunkt = datenpunkte[0]
                anzahl_widerstaende = len(beispiel_datenpunkt) - 2  # - Zeitpunkt, - Temperatur
                widerstand_counts[board_name] = anzahl_widerstaende

            # Erstelle eine Liste von Dictionaries für jeden Messpunkt
            daten = []
            for messpunkt_index in range(max_messpunkte):
                messpunkt_daten = {'Messpunkt': messpunkt_index + 1}
                for board_name in sorted_boards:
                    board_status, datenpunkte = boards_data[board_name]
                    anzahl_widerstaende = widerstand_counts[board_name]
                    if messpunkt_index < len(datenpunkte):
                        datenpunkt = datenpunkte[messpunkt_index]
                        # Zeitpunkt ignorieren
                        widerstandswerte = datenpunkt[1:-1]
                        temperatur = datenpunkt[-1]
                        # Annahme: Nur ein Widerstand pro Board
                        messpunkt_daten[f'{board_name} Widerstand 1'] = widerstandswerte[0] if widerstandswerte else None
                        messpunkt_daten[f'{board_name} Temperatur'] = temperatur
                    else:
                        # Fehlende Daten mit None auffüllen
                        messpunkt_daten[f'{board_name} Widerstand 1'] = None
                        messpunkt_daten[f'{board_name} Temperatur'] = None
                daten.append(messpunkt_daten)

            # Erstelle den DataFrame
            df = pd.DataFrame(daten)

            # Berechne die gemittelte Temperatur für jede Zeile
            gemittelte_temperaturen = []
            for idx, row in df.iterrows():
                temperaturwerte = []
                for board_name in sorted_boards:
                    temp = row[f'{board_name} Temperatur']
                    if pd.notnull(temp):
                        temperaturwerte.append(temp)
                if temperaturwerte:
                    mittelwert = round(sum(temperaturwerte) / len(temperaturwerte), 2)
                else:
                    mittelwert = None
                gemittelte_temperaturen.append(mittelwert)
            df['Gemittelte Temperatur'] = gemittelte_temperaturen

            # Schreibe den DataFrame in die Excel-Datei ohne Header
            df.to_excel(writer, sheet_name=sheet_name_plot, index=False, header=False, startrow=3)
            worksheet = writer.sheets[sheet_name_plot]

            # Formate definieren
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#C6EFCE', 'border': 1})
            cell_format = workbook.add_format({'align': 'center', 'border': 1})

            # Erste Zeile: Titel
            header_title = f"Messwerte mit Boardtemperatur {sheet_name_plot}"
            total_columns = df.shape[1] - 1  # Subtrahiere 1, da DataFrame-Spalten bei 0 beginnen
            worksheet.merge_range(0, 0, 0, total_columns, header_title, header_format)

            # Zweite Zeile: 'Messpunkt', 'Board 1', 'Board 2', ..., 'Gemittelte Temperatur'
            worksheet.write(1, 0, 'Messpunkt', header_format)

            col = 1
            for board_name in sorted_boards:
                worksheet.merge_range(1, col, 1, col + 1, board_name, header_format)
                col += 2

            # Zusätzliche Spalte für 'Gemittelte Temperatur'
            worksheet.write(1, col, 'Gemittelte Temperatur', header_format)
            gemittelte_temperatur_col = col

            # Dritte Zeile: 'Widerstand 1', 'Temperatur', ..., ''
            worksheet.write(2, 0, '', header_format)
            col = 1
            for board_name in sorted_boards:
                worksheet.write(2, col, 'Widerstand 1', header_format)
                worksheet.write(2, col + 1, 'Temperatur', header_format)
                col += 2

            worksheet.write(2, col, '', header_format)

            # Daten formatieren
            max_row = 3 + len(df)
            for row_num in range(3, max_row):
                worksheet.set_row(row_num, None, cell_format)

            # Spaltenbreite anpassen
            for col_num in range(total_columns + 1):
                worksheet.set_column(col_num, col_num, 15)

            # Gemittelte Temperatur in Excel schreiben (bereits berechnet)
            for idx, mittelwert in enumerate(gemittelte_temperaturen):
                row_num = 3 + idx
                if mittelwert is not None:
                    worksheet.write_number(row_num, gemittelte_temperatur_col, mittelwert, cell_format)
                else:
                    worksheet.write(row_num, gemittelte_temperatur_col, '', cell_format)

            # Farben für Boards definieren
            colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']
            board_colors = {}
            for idx, board_name in enumerate(sorted_boards):
                color = colors[idx % len(colors)]
                board_colors[board_name] = color

            # Diagramme erstellen
            chart_row = max_row + 2
            for idx, board_name in enumerate(sorted_boards):
                # Farbe für dieses Board erhalten
                color = board_colors[board_name]

                # Spaltenindizes für Widerstand, Board-Temperatur und gemittelte Temperatur
                col_widerstand = 1 + idx * 2  # Widerstandsspalte
                col_temperatur = col_widerstand + 1  # Board-Temperaturspalte
                col_gemittelte_temperatur = gemittelte_temperatur_col  # Gemittelte Temperatur

                # Erstes Diagramm: Widerstand über Board-Temperatur
                chart1 = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                chart1.add_series({
                    'name':       board_name,
                    'categories': [sheet_name_plot, 3, col_temperatur, max_row - 1, col_temperatur],
                    'values':     [sheet_name_plot, 3, col_widerstand, max_row - 1, col_widerstand],
                    'marker':     {'type': 'circle', 'size': 7, 'fill': {'color': color}},
                    'line':       {'none': True},
                    'trendline': {
                        'type': 'linear',
                        'display_equation': True,
                        'display_r_squared': True,
                    },
                })
                chart1.set_title({'name': f"{board_name} - Widerstand über Board-Temperatur ({sheet_name_plot})"})
                chart1.set_x_axis({'name': 'Temperatur (°C)'})
                chart1.set_y_axis({'name': 'Widerstand (Ohm)'})
                chart1.set_legend({'none': True})

                # Zweites Diagramm: Widerstand über gemittelte Temperatur
                chart2 = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                chart2.add_series({
                    'name':       board_name,
                    'categories': [sheet_name_plot, 3, col_gemittelte_temperatur, max_row - 1, col_gemittelte_temperatur],
                    'values':     [sheet_name_plot, 3, col_widerstand, max_row - 1, col_widerstand],
                    'marker':     {'type': 'circle', 'size': 7, 'fill': {'color': color}},
                    'line':       {'none': True},
                    'trendline': {
                        'type': 'linear',
                        'display_equation': True,
                        'display_r_squared': True,
                    },
                })
                chart2.set_title({'name': f"{board_name} - Widerstand über Gemittelte Temperatur ({sheet_name_plot})"})
                chart2.set_x_axis({'name': 'Gemittelte Temperatur (°C)'})
                chart2.set_y_axis({'name': 'Widerstand (Ohm)'})
                chart2.set_legend({'none': True})

                # Diagramme nebeneinander platzieren
                chart1_cell = f"A{chart_row + idx * 20}"
                chart2_cell = f"M{chart_row + idx * 20}"

                worksheet.insert_chart(chart1_cell, chart1, {'x_scale': 1.5, 'y_scale': 1.5})
                worksheet.insert_chart(chart2_cell, chart2, {'x_scale': 1.5, 'y_scale': 1.5})

        # Erfolgsmeldung
        print(f"Excel-Datei wurde gespeichert unter: {file_path}")
