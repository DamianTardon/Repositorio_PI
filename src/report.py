import numpy as np
from fpdf import FPDF

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
        self.cell(0, 10, "Registro de Calibración del Software (según IEC 61083-2)", align="C", new_x="LMARGIN", new_y="NEXT")
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
        if not self.tdg_meta:
            raise ValueError("No se puede generar el reporte: Faltan los metadatos del TDG.")
        else:
            self.cell(0, 6, f"Generador de Datos de prueba (TDG): {self.tdg_meta.get('software_version', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
            self.cell(0, 6, f"Resolución TDG: {self.tdg_meta.get('resolution', 'N/A')} | Tasa de Muestreo (Rate): {self.tdg_meta.get('rate', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def add_results_table(self, results_li, results_lic):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, "2. Tabla de Resultados", new_x="LMARGIN", new_y="NEXT")

        self.set_font("helvetica", "B", 10)
        self.cell(0, 8, "2.1 Full Lightning Impulses - LI", new_x="LMARGIN", new_y="NEXT")
        self._draw_results_table(results_li)

        self.ln(5)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 8, "2.2 Chopped Lightning Impulses (LIC)", new_x="LMARGIN", new_y="NEXT")
        self._draw_results_table(results_lic)

    def _draw_results_table(self, results_data):
        if not results_data:
            self.set_font("helvetica", "I", 10)
            self.cell(0, 6, "No hay datos registrados para esta categoría.", new_x="LMARGIN", new_y="NEXT")
            return

        # Cabeceras de tabla.
        self.set_font("helvetica", "B", 8)
        col_widths = [23, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        # Coordenada X inicial para saber dónde volver en la 2da fila.
        x_start = self.get_x()

        # Fila 1 de la Cabecera.
        self.cell(col_widths[0], 12, "Onda", border=1, align="C")
        for param in ["Ut [kV]", "T1 [µs]", "T2/Tc [µs]", "OS [%]"]:
            self.cell(60, 6, param, border=1, align="C")
        self.ln()

        # Fila 2 de la Cabecera.
        self.set_x(x_start + col_widths[0])
        sub_headers = ["ref", "calc", "Desv"] * 4
        for i, header in enumerate(sub_headers):
            if i == len(sub_headers) - 1:
                self.cell(col_widths[i+1], 6, header, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
            else:
                self.cell(col_widths[i+1], 6, header, border=1, align="C")

        # Filas de Datos.
        self.set_font("helvetica", "", 8)
        params_info = [('U', 2), ('T1', 3), ('T2', 2), ('OS', 2)] 

        for row in results_data:
            self.cell(col_widths[0], 6, row['file_id'], border=1, align="C")

            for p_idx, (p_key, decimals) in enumerate(params_info):
                ref = row[f'{p_key}_ref']
                calc = row[f'{p_key}_calc']
                desv = row[f'{p_key}_desv']

                str_ref = f"{ref:.{decimals}f}" if not np.isnan(ref) else "N/A"
                str_calc = f"{calc:.{decimals}f}" if not np.isnan(calc) else "N/A"
                str_desv = f"{desv:.3f}%" if not np.isnan(desv) else "N/A"

                base_idx = 1 + (p_idx * 3)
                self.cell(col_widths[base_idx], 6, str_ref, border=1, align="C")
                self.cell(col_widths[base_idx+1], 6, str_calc, border=1, align="C")
                self.cell(col_widths[base_idx+2], 6, str_desv, border=1, align="C")
            self.ln()
        self.ln(5)

    def add_uncertainty_table(self, uncertainty_li, uncertainty_lic):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, "3. Estimación de Incertidumbre (según Anexo B.3.3)", new_x="LMARGIN", new_y="NEXT")

        self.set_font("helvetica", "", 10)
        self.cell(0, 6, "Basado en las máximas desviaciones encontradas:", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font("helvetica", "B", 10)
        self.cell(0, 6, "3.1 Full Lightning Impulses - LI", new_x="LMARGIN", new_y="NEXT")
        self._draw_uncertainty_table(uncertainty_li)

        self.ln(5)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 6, "3.2 Chopped Lightning Impulses (LIC)", new_x="LMARGIN", new_y="NEXT")
        self._draw_uncertainty_table(uncertainty_lic)

    def _draw_uncertainty_table(self, uncertainty_results):
        # Valida que al menos haya algún dato real evaluado en el diccionario antes de dibujarlo.
        has_data = any(not np.isnan(vals[2]) for vals in uncertainty_results.values() if vals)

        if not has_data:
            self.set_font("helvetica", "I", 10)
            self.cell(0, 6, "No hay datos suficientes para calcular incertidumbre.", new_x="LMARGIN", new_y="NEXT")
            return

        # Cabeceras de la tabla de incertidumbre.
        self.set_font("helvetica", "B", 9)
        col_widths = [45, 45, 45, 45]
        for header in ["Parámetro", "u_B71 (Software) [%]", "u_B72 (Referencia) [%]", "u_B7 (Combinada) [%]"]:
            self.cell(45, 6, header, border=1, align="C")
        self.ln()

        # Mapeo de parámetros a mostrar.
        self.set_font("helvetica", "", 9)
        param_names = [
            ("U", "Valor Pico (Ut)"),
            ("T1", "Tiempo de Frente (T1)"), 
            ("T2", "Tiempo de Cola (T2/Tc)"),
            ("OS", "Sobrepasamiento (OS)")]

        for key, name in param_names:
            u_B71, u_B72, u_B7 = uncertainty_results[key]
            self.cell(col_widths[0], 6, name, border=1, align="C")

            # Validación por si el parámetro no aplica (ej. todo NaN).
            if np.isnan(u_B7):
                self.cell(col_widths[1], 6, "N/A", border=1, align="C")
                self.cell(col_widths[2], 6, "N/A", border=1, align="C")
                self.cell(col_widths[3], 6, "N/A", border=1, align="C")
            else:
                self.cell(col_widths[1], 6, f"{u_B71:.4f}", border=1, align="C")
                self.cell(col_widths[2], 6, f"{u_B72:.4f}", border=1, align="C")
                self.set_font("helvetica", "B", 9)
                self.cell(col_widths[3], 6, f"{u_B7:.4f}", border=1, align="C")
                self.set_font("helvetica", "", 9)
            self.ln()