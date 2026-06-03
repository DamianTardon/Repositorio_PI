from __future__ import annotations
import numpy as np
from fpdf import FPDF
from typing import Dict, List, Any

def print_information_TDG(metadata: Dict[str, Any], data: List[float]) -> None:
    """Imprime por consola los metadatos y la longitud de la forma de onda extraída de un archivo TDG.

    Utilidad de depuración para auditar la correcta lectura de los archivos de calibración del 
    Test Data Generator (TDG).

    Args:
        metadata (Dict[str, Any]): Diccionario con los metadatos del archivo TDG (versión, resolución, etc.).
        data (List[float]): Lista unidimensional con los valores de tensión de la onda.
    """
    ...

class ReportPDF(FPDF):
    """Generador de reportes PDF para la calibración del software según la norma IEC 61083-2.

    Extiende la funcionalidad de `fpdf.FPDF` para renderizar tablas tabulares complejas, metadatos 
    ambientales y cálculos de incertidumbre ($u_{B71}$, $u_{B72}$, $u_{B7}$) del analizador de impulsos.
    Configurado estructuralmente en orientación apaisada (Landscape) para formato A4.

    Attributes:
        software_meta (Dict[str, Any]): Diccionario con los metadatos del analizador de impulsos a validar.
        tdg_meta (Dict[str, Any]): Diccionario con los metadatos del generador de datos de prueba (TDG).
    """

    def __init__(self, software_meta: Dict[str, Any], tdg_meta: Dict[str, Any]) -> None:
        """Inicializa el documento PDF en formato apaisado A4, ajusta márgenes y almacena los metadatos.

        Args:
            software_meta (Dict[str, Any]): Información del software evaluado (nombre, algoritmos, parámetros).
            tdg_meta (Dict[str, Any]): Información del simulador TDG de referencia.
        """
        ...

    def header(self) -> None:
        """Sobrescribe el método de la clase base `FPDF` para renderizar el encabezado en cada página.

        Imprime el título normativo del registro de calibración.
        """
        ...

    def add_metadata_section(self) -> None:
        """Construye la sección '1. Información de la Validación'.

        Imprime las versiones de los sistemas, algoritmos soportados y el set de parámetros a validar.
        """
        ...

    def add_results_table(self, results_li: List[Dict[str, Any]], results_lic: List[Dict[str, Any]]) -> None:
        """Construye la sección '2. Tabla de Resultados' separando impulsos plenos y cortados.

        Args:
            results_li (List[Dict[str, Any]]): Estructura de resultados comparativos para Full Lightning Impulses (LI).
            results_lic (List[Dict[str, Any]]): Estructura de resultados comparativos para Chopped Lightning Impulses (LIC).
        """
        ...

    def _draw_results_table(self, results_data: List[Dict[str, Any]]) -> None:
        """Renderiza las celdas, bordes y filas de la tabla paramétrica comparativa.

        Despliega las columnas de $U_t$, $T_1$, $T_2$ y OS, contrastando los valores de referencia 
        (TDG) contra los calculados, e incluyendo el porcentaje de desviación.

        Args:
            results_data (List[Dict[str, Any]]): Lista de diccionarios con métricas por cada archivo de onda procesado.
        """
        ...

    def add_uncertainty_table(self, uncertainty_li: Dict[str, Tuple[float, float, float]], uncertainty_lic: Dict[str, Tuple[float, float, float]]) -> None:
        """Construye la sección '3. Estimación de Incertidumbre' según el Anexo B.3.3 de la norma IEC 61083-2.

        Args:
            uncertainty_li (Dict[str, Tuple[float, float, float]]): Resultados de incertidumbre para ondas tipo LI.
            uncertainty_lic (Dict[str, Tuple[float, float, float]]): Resultados de incertidumbre para ondas tipo LIC.
        """
        ...

    def _draw_uncertainty_table(self, uncertainty_results: Dict[str, Tuple[float, float, float]]) -> None:
        """Renderiza la tabla de estimación de incertidumbres paramétricas.

        Desglosa y grafica los valores de la incertidumbre aportada por el software ($u_{B71}$), 
        la incertidumbre de la referencia ($u_{B72}$), y la incertidumbre combinada final ($u_{B7}$).

        Args:
            uncertainty_results (Dict[str, Tuple[float, float, float]]): Diccionario que asocia la clave del parámetro 
                (ej. 'U', 'T1') con la tupla resultante ($u_{B71}$, $u_{B72}$, $u_{B7}$).
        """
        ...