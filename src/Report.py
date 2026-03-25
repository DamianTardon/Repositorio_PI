import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

def print_information_TDG(metadata, data):
    print(f"Versión de TDG: {metadata['software_version']}")
    print(f"Versión de archivo de datos: {metadata['version_file']}")
    print(f"Nombre de onda: {metadata['wave_name']}")
    print(f"Resolución de datos: {metadata['resolution']}")
    print(f"Cantidad de muestras: {metadata['samples']}")
    print(f"Intervalo de muestreo: {metadata['interval']}")
    print(f"Tasa de muestreo: {metadata['rate']}")
    print("Datos de la onda:")
    print(f"\nTotal de puntos extraídos: {len(data)}")

def plot_1_waveform(time_axis1, waveform1, label1, title):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis1, waveform1, label=label1)
    plt.title(title)
    plt.legend()
    plt.xlabel("Tiempo [µs]")
    plt.ylabel("Tensión [kV]")
    plt.grid(True)
    plt.show()

def plot_2_waveform(time_axis1, waveform1, label1, time_axis2, waveform2, label2, title):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis1, waveform1, label=label1)
    plt.plot(time_axis2, waveform2, color='red',label=label2)
    plt.title(title)
    plt.legend()
    plt.xlabel("Tiempo [µs]")
    plt.ylabel("Tensión [kV]")
    plt.grid(True)
    plt.show()

class ReportPDF(FPDF):
    def __init__(self, software_meta, tdg_meta):
        # Apaisado para acomodar la tabla.
        super().__init__(orientation="L", unit="mm", format="A4")
        self.software_meta = software_meta
        self.tdg_meta = tdg_meta
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        # Título principal.
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "Registro de Calibración del Software (IEC 61083-2)", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def add_metadata_section(self):
        # Subtítulo.
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, "1. Información de la Validación", new_x="LMARGIN", new_y="NEXT")

        # Software.
        self.set_font("helvetica", "", 10)
        self.cell(0, 6, f"Software Probado: {self.software_meta['name']} (v{self.software_meta['version']}) - {self.software_meta['date']}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Algoritmos soportados: {', '.join(self.software_meta['algorithms'])}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Parámetros validados: {', '.join(self.software_meta['parameters'])}", new_x="LMARGIN", new_y="NEXT")

        # TDG.
        self.ln(2)
        if self.tdg_meta:
            self.cell(0, 6, f"Generador de Datos (TDG): {self.tdg_meta.get('software_version', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
            self.cell(0, 6, f"Resolución TDG: {self.tdg_meta.get('resolution', 'N/A')} | Tasa de Muestreo (Rate): {self.tdg_meta.get('rate', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def add_results_table(self, results_data):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, "2. Tabla de Resultados (Full Lightning Impulse - LI)", new_x="LMARGIN", new_y="NEXT")

        # Cabeceras de tabla.
        self.set_font("helvetica", "B", 8)
        col_widths = [23, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        headers = [
            "Onda", 
            "Ut Ref [kV]", "Ut Calc", "Desv. Ut", 
            "T1 Ref [µs]", "T1 Calc", "Desv. T1", 
            "T2 Ref [µs]", "T2 Calc", "Desv. T2", 
            "OS Ref [%]", "OS Calc", "Desv. OS"
        ]

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, align="C")
        self.ln()

        # Filas de datos.
        self.set_font("helvetica", "", 8)
        for row in results_data:
            self.cell(col_widths[0], 8, row['file_id'], border=1, align="C")

            self.cell(col_widths[1], 8, f"{row['ref_peak']:.2f}", border=1, align="C")
            self.cell(col_widths[2], 8, f"{row['calc_peak']:.2f}", border=1, align="C")
            self.cell(col_widths[3], 8, f"{row['dev_peak']:.3f}%", border=1, align="C")

            self.cell(col_widths[4], 8, f"{row['ref_t1']:.3f}", border=1, align="C")
            self.cell(col_widths[5], 8, f"{row['calc_t1']:.3f}", border=1, align="C")
            self.cell(col_widths[6], 8, f"{row['dev_t1']:.3f}%", border=1, align="C")

            self.cell(col_widths[7], 8, f"{row['ref_t2']:.2f}", border=1, align="C")
            self.cell(col_widths[8], 8, f"{row['calc_t2']:.2f}", border=1, align="C")
            self.cell(col_widths[9], 8, f"{row['dev_t2']:.3f}%", border=1, align="C")

            ref_beta_str = f"{row['ref_beta']:.2f}" if not np.isnan(row['ref_beta']) else "N/A"
            calc_beta_str = f"{row['calc_beta']:.2f}" if not np.isnan(row['calc_beta']) else "N/A"
            dev_beta_str = f"{row['dev_beta']:.3f}%" if not np.isnan(row['dev_beta']) else "N/A"

            self.cell(col_widths[10], 8, ref_beta_str, border=1, align="C")
            self.cell(col_widths[11], 8, calc_beta_str, border=1, align="C")
            self.cell(col_widths[12], 8, dev_beta_str, border=1, align="C")
            self.ln()

        self.ln(5)

    def add_uncertainty_calculations(self, unc_results):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, "3. Estimación de Incertidumbre (Anexo B.3.3)", new_x="LMARGIN", new_y="NEXT")

        self.set_font("helvetica", "", 10)
        self.cell(0, 6, "Basado en las máximas desviaciones encontradas:", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # Cabeceras de la mini-tabla de incertidumbre.
        self.set_font("helvetica", "B", 9)
        col_widths = [45, 45, 45, 45]
        headers = ["Parámetro", "u_B71 (Software) [%]", "u_B72 (Referencia) [%]", "u_B7 (Combinada) [%]"]

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, align="C")
        self.ln()

        self.set_font("helvetica", "", 9)

        # Mapeo de claves a nombres para mostrar.
        param_names = {
            "Ut": "Valor Pico (Ut)",
            "T1": "Tiempo de Frente (T1)",
            "T2": "Tiempo de Cola (T2)",
            "Beta": "Sobrepasamiento (OS)"
        }

        for key, name in param_names.items():
            u_B71, u_B72, u_B7 = unc_results[key]

            self.cell(col_widths[0], 8, name, border=1, align="C")

            # Validación por si el parámetro no aplica (ej. todo NaN).
            if np.isnan(u_B7):
                self.cell(col_widths[1], 8, "N/A", border=1, align="C")
                self.cell(col_widths[2], 8, "N/A", border=1, align="C")
                self.cell(col_widths[3], 8, "N/A", border=1, align="C")
            else:
                self.cell(col_widths[1], 8, f"{u_B71:.4f}", border=1, align="C")
                self.cell(col_widths[2], 8, f"{u_B72:.4f}", border=1, align="C")

                # Resaltamos en negrita el resultado final u_B7.
                self.set_font("helvetica", "B", 9)
                self.cell(col_widths[3], 8, f"{u_B7:.4f}", border=1, align="C")
                self.set_font("helvetica", "", 9) # Volvemos a normal para la siguiente fila.
            self.ln()

        self.ln(5)