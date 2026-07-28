r"""Módulo de generación de reportes técnicos normativos en formato PDF.

Automatiza la construcción de informes de calibración cumpliendo con la 
norma IEC 61083-2, empleando el motor de renderizado FPDF.
"""

from __future__ import annotations

import numpy as np
from fpdf import FPDF

# Importaciones exclusivas para el tipado estático en la documentación.
from typing import Dict, List, Any, Tuple, Union


def print_information_TDG(
        metadata: Dict[str, Union[str, int]], 
        data: np.ndarray
) -> None:
    r"""Imprime por consola los metadatos y la longitud de la forma de 
    onda extraída de un archivo TDG.

    Utilidad de depuración para auditar la correcta lectura de los 
    archivos de calibración del Test Data Generator (TDG).

    Args:
        metadata (Dict[str, Union[str, int]]): Metadatos del archivo TDG.
            Debe contener obligatoriamente el siguiente esquema de claves:
            
            - ``'software_version'`` (str): Versión del software 
                generador de datos.
            - ``'version_file'`` (str): Versión del archivo de onda.
            - ``'wave_name'`` (str): Nombre de la forma de onda.
            - ``'resolution'`` (str): Resolución digital de la onda en 
                :math:`\text{bit}`.
            - ``'samples'`` (int): Cantidad total de muestras registradas.
            - ``'interval'`` (str): Periodo entre muestras sucesivas.
            - ``'rate'`` (str): Tasa de muestreo del sistema de adquisición.
            
        data (np.ndarray): Estructura unidimensional con los valores 
            discretos de tensión de la onda.

    Raises:
        KeyError: Si el diccionario ``metadata`` carece de alguna de las 
            claves obligatorias requeridas.
    """
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
    r"""Generador de reportes PDF para la calibración del software 
    según la norma IEC 61083-2.

    Extiende la funcionalidad de :class:`fpdf.FPDF` para renderizar tablas
    de resultados, metadatos ambientales y cálculos de incertidumbre. 
    Configurado en formato A4 en orientación vertical.

    Attributes:
        software_meta (Dict[str, Any]): Diccionario con los metadatos 
            del analizador de impulsos a validar.
            Esquema de claves:
            
            - ``'name'`` (str): Nombre del software o módulo bajo prueba.
            - ``'version'`` (str): Versión del software.
            - ``'date'`` (str): Fecha de ejecución del ensayo de validación.
            - ``'algorithms'`` (List[str]): Algoritmos matemáticos 
                soportados (Full Lightning Impulse (LI), 
                Chopped Lightning Impulse (LIC)).
            - ``'parameters'`` (List[str]): Parámetros del impulso que 
                el software puede validar.
            
        tdg_meta (Dict[str, Any]): Diccionario con los metadatos del 
            generador de datos de prueba (TDG).
            Esquema obligatorio de claves:
            
            - ``'software_version'`` (str): Versión del software TDG.
            - ``'resolution'`` (str): Resolución digital de la onda en 
                :math:`\text{bit}`.
            - ``'rate'`` (str): Tasa de muestreo de la referencia.
    """

    def __init__(
            self, 
            software_meta: Dict[str, Any], 
            tdg_meta: Dict[str, Any]
    ) -> None:
        r"""Inicializa el documento PDF en formato vertical A4, ajusta 
        márgenes y almacena los metadatos.

        Args:
            software_meta (Dict[str, Any]): Metadatos del software evaluado.
                Ver esquema requerido en la documentación de la clase 
                :class:`ReportPDF`.
            tdg_meta (Dict[str, Any]): Metadatos del TDG de referencia.
                Ver esquema requerido en la documentación de la clase 
                :class:`ReportPDF`.
        """
        # Hoja A4 apaisada.
        super().__init__(orientation="P", unit="mm", format="A4")
        self.software_meta = software_meta
        self.tdg_meta = tdg_meta
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self) -> None:
        r"""Sobrescribe el método base de la clase :class:`fpdf.FPDF` 
        para renderizar el encabezado normativo.

        Genera el título principal centrado en tipografía Helvética, con 
        estilo negrita de tamaño 16 y un espaciado inferior.

        .. note::
            Este método es un *override* (sobrescritura) nativo de la 
            clase base. Es invocado automáticamente por la librería FPDF 
            cada vez que se crea una nueva página (ej.: ``add_page()``).
            No debe ser invocado manualmente por el usuario en el flujo 
            del código.
        """
        # Título principal.
        self.set_font("helvetica", "B", 16)
        self.cell(
            0,
            10,
            "Registro de Calibración del Software (según IEC 61083-2)",
            align="C",
            new_x="LMARGIN",new_y="NEXT"
        )
        
        self.ln(5)

    def add_metadata_section(self) -> None:
        r"""Construye y renderiza en el PDF la sección de metadatos del 
        software evaluado y del TDG.

        Dibuja en el documento los metadatos del software evaluado, sus 
        algoritmos y el conjunto de parámetros validados, 
        complementándolo con las especificaciones del TDG de referencia.

        Raises:
            ValueError: Si los metadatos del generador de datos de prueba 
                (TDG) no están presentes (``self.tdg_meta`` está vacío 
                o es nulo). La norma IEC 61083-2 exige documentar la 
                referencia utilizada. Esto asegura que el reporte no se 
                genere de forma incompleta.
            KeyError: Si los diccionarios internos de metadatos carecen 
                de las claves requeridas para el renderizado de la 
                sección en el PDF.
        """
        # Subtítulo.
        self.set_font("helvetica", "B", 12)
        self.cell(
            0,
            8,
            "1. Información de la Validación",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        # Software.
        self.set_font("helvetica", "", 10)
    
        name = self.software_meta['name']
        version = self.software_meta['version']
        date = self.software_meta['date']
        algorithms = ", ".join(self.software_meta['algorithms'])
        parameters = ", ".join(self.software_meta['parameters'])

        self.cell(
            0,
            6,
            f"Software Probado: {name} (v{version}) - {date}",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self.cell(
            0,6,
            f"Algoritmos soportados: {algorithms}",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self.cell(
            0,
            6,
            f"Parámetros validados: {parameters}",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        # TDG.
        if not self.tdg_meta:
            raise ValueError("No se puede generar el reporte: "
                             "Faltan los metadatos del TDG.")
        else:
            software_version = self.tdg_meta.get('software_version', 'N/A')
            resolution = self.tdg_meta.get('resolution', 'N/A')
            rate = self.tdg_meta.get('rate', 'N/A')

            self.cell(
                0,
                6,
                f"Generador de Datos de prueba (TDG): {software_version}",
                new_x="LMARGIN",
                new_y="NEXT"
            )
            self.cell(
                0,
                6,
                f"Resolución TDG: {resolution} | Tasa de Muestreo: {rate}",
                new_x="LMARGIN",
                new_y="NEXT")
        self.ln(5)

    def add_results_table(
            self, 
            results_li: List[Dict[str, Union[str, float]]], 
            results_lic: List[Dict[str, Union[str, float]]]
    ) -> None:
        r"""Construye la sección de resultados, separando impulsos 
        plenos y cortados.

        Dibuja de forma secuencial los subtítulos y renderiza la tabla 
        de las métricas de impulsos plenos (LI) 
        (:math:`\qty{1.2/50}{\micro\second}`) e impulsos cortados (LIC).

        Args:
            results_li (List[Dict[str, Union[str, float]]]): 
                Estructura de resultados para Full Lightning Impulses (LI).
                Cada elemento de la lista debe cumplir con el esquema 
                documentado en :meth:`_draw_results_table`.
            results_lic (List[Dict[str, Union[str, float]]]): 
                Estructura de resultados para Chopped Lightning Impulses 
                (LIC). Cada elemento de la lista debe cumplir con el 
                esquema documentado en :meth:`_draw_results_table`.
        """
        self.set_font("helvetica", "B", 12)
        self.cell(
            0,
            8,
            "2. Tabla de Resultados",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        self.set_font("helvetica", "B", 10)
        self.cell(
            0,
            8,
            "2.1 Full Lightning Impulses - LI",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self._draw_results_table(results_li)

        self.ln(5)
        self.set_font("helvetica", "B", 10)
        self.cell(
            0,
            8,
            "2.2 Chopped Lightning Impulses (LIC)",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self._draw_results_table(results_lic)

    def _draw_results_table(
            self, 
            results_data: List[Dict[str, Union[str, float]]]
    ) -> None:
        r"""Renderiza la tabla de resultados en el documento PDF.

        Despliega una tabla de resultados que contiene los valores de 
        referencia (TDG), los calculados por el software bajo prueba, y 
        el error relativo.
        La cabecera de la tabla se compone de una primera fila con las 
        magnitudes calculadas:
            - Tensión de pico (:math:`U_{\text{t}}`).
            - Tiempo de frente (:math:`T_1`).
            - Tiempo de cola/corte (:math:`T_2` o :math:`T_{\text{c}}`).
            - Sobrepasamiento relativo (:math:`\text{OS}`).
        La segunda fila subdivide cada parámetro en las columnas:
            - Valor de referencia (``Ref``).
            - Valor calculado (``Calc``).
            - Desviación porcentual (``Desv``).

        .. note::
            **Mecanismo de Contingencia**: Si la lista ``results_data`` 
            está vacía o es nula, aborta el dibujo de la tabla y 
            renderiza un mensaje alternativo de advertencia:
            "No hay datos registrados para esta categoría.".

            **Formateo de Valores Nulos (NaN)**: El algoritmo intercepta 
            valores nulos (:math:`\text{NaN}`) de cálculos previos y los 
            renderiza como una cadena de caracteres ``"N/A"``. Evita 
            excepciones de manipulación de strings en FPDF.

        Args:
            results_data (List[Dict[str, Union[str, float]]]): Lista de 
                resultados por archivo procesado.
                Cada diccionario contiene las siguientes claves:

                - ``'file_id'`` (str): Nombre de la onda analizada.
                - ``'U_ref'``, ``'U_calc'``, ``'U_deviation'`` (float): 
                  Tensión de pico :math:`U_{\text{t}}` (referencia, 
                  calculado y desviación). 
                  Tensión en :math:`\unit{\kilo\volt}`, 
                  desviación en :math:`\unit{\percent}`.
                - ``'T1_ref'``, ``'T1_calc'``, ``'T1_deviation'`` (float): 
                  Tiempo de frente :math:`T_1` (referencia, calculado y 
                  desviación). 
                  Tiempo en :math:`\unit{\micro\second}`, 
                  desviación en :math:`\unit{\percent}`.
                - ``'T2_ref'``, ``'T2_calc'``, ``'T2_deviation'`` (float): 
                  Tiempo de cola :math:`T_2` (referencia, calculado y 
                  desviación). 
                  Tiempo en :math:`\unit{\micro\second}`, 
                  desviación en :math:`\unit{\percent}`.
                - ``'OS_ref'``, ``'OS_calc'``, ``'OS_deviation'`` (float): 
                  Sobrepasamiento :math:`\text{OS}` (referencia, 
                  calculado y desviación). 
                  Todos los valores en :math:`\unit{\percent}`.

        Raises:
            KeyError: Si los diccionarios de resultados no contienen 
                las claves declaradas.
        """
        if not results_data:
            self.set_font("helvetica", "I", 10)
            self.cell(
                0,
                6,
                "No hay datos registrados para esta categoría.",
                new_x="LMARGIN",
                new_y="NEXT"
            )
            return

        # Cabeceras de tabla.
        self.set_font("helvetica", "B", 8)
        col_widths = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        # Coordenada X inicial para iniciar la 2da fila.
        x_start = self.get_x()

        # Fila 1 (Cabecera).
        self.cell(col_widths[0], 12, "Onda", border=1, align="C")
        for param in ["Ut [kV]", "T1 [µs]", "T2/Tc [µs]", "OS [%]"]:
            self.cell(45, 6, param, border=1, align="C")
        self.ln()

        # Fila 2 (Cabecera).
        self.set_x(x_start + col_widths[0])
        sub_headers = ["Ref", "Calc", "Desv"] * 4
        for i, header in enumerate(sub_headers):
            if i == len(sub_headers) - 1:
                self.cell(
                    col_widths[i+1],
                    6,
                    header,
                    border=1,
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT"
                )
            else:
                self.cell(col_widths[i+1], 6, header, border=1, align="C")

        # Filas de Datos.
        self.set_font("helvetica", "", 8)
        params_info = [('U', 2), ('T1', 3), ('T2', 2), ('OS', 2)] 

        for row in results_data:
            self.cell(
                col_widths[0],
                6,
                str(row['file_id']),
                border=1,
                align="C"
            )

            for p_idx, (p_key, decimals) in enumerate(params_info):
                raw_ref = row[f'{p_key}_ref']
                raw_calc = row[f'{p_key}_calc']
                raw_deviation = row[f'{p_key}_deviation']

                # Conversión segura para el análisis estático.
                if isinstance(raw_ref, (int, float)):
                    ref = float(raw_ref)
                else:
                    ref = np.nan

                if isinstance(raw_calc, (int, float)):
                    calc = float(raw_calc)
                else:
                    calc = np.nan

                if isinstance(raw_deviation, (int, float)):
                    desv = float(raw_deviation)
                else:
                    desv = np.nan

                str_ref = f"{ref:.{decimals}f}" if not np.isnan(ref) else "N/A"
                str_calc = f"{calc:.{decimals}f}" if not np.isnan(calc) else "N/A"
                str_deviation = f"{desv:.3f}%" if not np.isnan(desv) else "N/A"

                base_idx = 1 + (p_idx * 3)
                self.cell(
                    col_widths[base_idx],
                    6,
                    str_ref,
                    border=1,
                    align="C"
                )
                self.cell(
                    col_widths[base_idx+1],
                    6,
                    str_calc,
                    border=1,
                    align="C"
                )
                self.cell(
                    col_widths[base_idx+2],
                    6,
                    str_deviation,
                    border=1,
                    align="C"
                )
            self.ln()
        self.ln(5)

    def add_uncertainty_table(
            self, 
            uncertainty_li: Dict[str, Tuple[float, float, float]], 
            uncertainty_lic: Dict[str, Tuple[float, float, float]]
    ) -> None:
        r"""Construye la sección de incertidumbres, separando impulsos 
        plenos y cortados.

        Dibuja de forma secuencial los subtítulos y renderiza la tabla
        de las incertidumbres de medición para cada parámetro, 
        determinado a partir del error máximo contra la referencia (TDG).
        Despliega una tabla de resultados por cada grupo de ondas (LI y LIC).

        Args:
            uncertainty_li (Dict[str, Tuple[float, float, float]]): 
                Incertidumbres calculadas para ondas plenas (LI). Las 
                claves del diccionario son: 
                ``'U'``, ``'T1'``, ``'T2'``, y ``'OS'``.
                Cada clave está asociada a una tupla de tres números 
                decimales, descriptos en :meth:`_draw_uncertainty_table`.
            uncertainty_lic (Dict[str, Tuple[float, float, float]]): 
                Incertidumbres calculadas para ondas cortadas (LIC).
                Las claves del diccionario son las mismas de 
                ``uncertainty_li``.
        """
        self.set_font("helvetica", "B", 12)
        self.cell(
            0,
            8,
            "3. Estimación de Incertidumbre (según Anexo B.3.3)",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        self.set_font("helvetica", "", 10)
        self.cell(
            0,
            6,
            "Basado en las máximas desviaciones encontradas:",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self.ln(2)

        self.set_font("helvetica", "B", 10)
        self.cell(
            0,
            6,
            "3.1 Full Lightning Impulses - LI",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self._draw_uncertainty_table(uncertainty_li)

        self.ln(5)
        self.set_font("helvetica", "B", 10)
        self.cell(
            0,
            6,
            "3.2 Chopped Lightning Impulses (LIC)",
            new_x="LMARGIN",
            new_y="NEXT"
        )
        self._draw_uncertainty_table(uncertainty_lic)

    def _draw_uncertainty_table(
            self, 
            uncertainty_results: Dict[str, Tuple[float, float, float]]
    ) -> None:
        r"""Renderiza la tabla de incertidumbres en el documento PDF.

        Despliega una tabla de las incertidumbres de cada parámetro de 
        la onda:

        - Incertidumbre del software bajo calibración (:math:`u_{\text{B}71}`).
        - Incertidumbre de la referencia / TDG (:math:`u_{\text{B}72}`).
        - Incertidumbre combinada estándar final (:math:`u_{\text{B}7}`) 
          obtenida mediante la suma en cuadratura.

        .. note::
            **Mecanismo de Contingencia**: Si en ``uncertainty_results`` 
            la incertidumbre combinada final (:math:`u_{\text{B}7}`) de 
            todos los parámetros es nula (:math:`\text{NaN}`), se aborta 
            la construcción de la tabla y se renderiza en su lugar el 
            mensaje de advertencia:
            "No hay datos suficientes para calcular incertidumbre."

        Args:
            uncertainty_results (Dict[str, Tuple[float, float, float]]): 
                Diccionario de parámetros normativos. Las claves válidas 
                son:

                - ``'U'``: Valor Pico (:math:`U_{\text{t}}`).
                - ``'T1'``: Tiempo de Frente (:math:`T_1`).
                - ``'T2'``: Tiempo de Cola (:math:`T_2` o 
                  :math:`T_{\text{c}}`).
                - ``'OS'``: Sobrepasamiento relativo (:math:`\text{OS}`).

                Cada clave mapea a una tupla de tres elementos del tipo 
                float que representan las incertidumbres en 
                :math:`\unit{\percent}`:

                - **Índice 0**: :math:`u_{\text{B}71}` (Incertidumbre 
                  del software).
                - **Índice 1**: :math:`u_{\text{B}72}` (Incertidumbre 
                  del TDG).
                - **Índice 2**: :math:`u_{\text{B}7}` (Incertidumbre 
                  combinada).

        Raises:
            KeyError: Si el diccionario de entrada carece de alguno de 
                los identificadores de parámetro esperados (``'U'``, 
                ``'T1'``, ``'T2'`` o ``'OS'``).
        """
        # Valida que al menos haya algún dato real evaluado 
        # en el diccionario antes de dibujarlo.
        has_data = any(
            not np.isnan(vals[2]) 
            for vals in uncertainty_results.values() if vals
        )

        if not has_data:
            self.set_font("helvetica", "I", 10)
            self.cell(
                0, 
                6, 
                "No hay datos suficientes para calcular incertidumbre.", 
                new_x="LMARGIN", 
                new_y="NEXT"
            )
            return

        # Cabeceras de la tabla de incertidumbre.
        self.set_font("helvetica", "B", 9)
        col_widths = [45, 45, 45, 45]

        UNCERTAINTY_HEADERS = (
            "Parámetro",
            "u_B71 (Software) [%]",
            "u_B72 (Referencia) [%]",
            "u_B7 (Combinada) [%]",
        )

        CELL_WIDTH = 45
        CELL_HEIGHT = 6
        BORDER_ALL = 1
        ALIGN_CENTER = "C"

        for header in UNCERTAINTY_HEADERS:
            self.cell(
                w=CELL_WIDTH,
                h=CELL_HEIGHT,
                text=header,
                border=BORDER_ALL,
                align=ALIGN_CENTER
            )
        self.ln()

        # Mapeo de parámetros a mostrar.
        self.set_font("helvetica", "", 9)
        PARAM_NAMES = [
            ("U", "Valor Pico (Ut)"),
            ("T1", "Tiempo de Frente (T1)"), 
            ("T2", "Tiempo de Cola (T2/Tc)"),
            ("OS", "Sobrepasamiento (OS)")
        ]

        for key, name in PARAM_NAMES:
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