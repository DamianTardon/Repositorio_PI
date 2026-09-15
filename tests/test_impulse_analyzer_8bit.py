r"""Módulo de pruebas unitarias automatizadas y calibración según la 
norma IEC 61083-2.

Diseñado bajo la arquitectura Pytest para validar la precisión del motor 
matemático del analizador inyectándole los conjuntos de datos de 
calibración patrón de la norma IEC.
"""

from __future__ import annotations

import pytest
from pathlib import Path
import numpy as np

from report import ReportPDF
from file_manager import FileManager
from impulse_analyzer import (
    LightningImpulseAnalyzer, 
    __app_name__, 
    __version__, 
    __release_date__, 
    __algorithms_supported__, 
    __parameters_validated__
)

from .test_cases_data import (
    TEST_CASES_LI, 
    UNCERTAINTY_CASES_LI, 
    TEST_CASES_LIC, 
    UNCERTAINTY_CASES_LIC, 
    ImpulseCase, 
    UncertaintyCase
)

# Importaciones exclusivas para el tipado estático en la documentación.
from typing import Dict, List, Any, Generator

BASE_DIR = Path(__file__).resolve().parent.parent / 'Calibracion' / 'IEC61083_2'


def _calc_uB7(
        dataset: List[Dict[str, Any]], 
        deviation_key: str, 
        urefs_key: str
) -> tuple[float, float, float]:
    r"""Función matemática auxiliar para calcular las incertidumbres 
    (IEC 61083-2).

    Extrae los valores máximos de desviación e incertidumbre de 
    referencia de un conjunto de datos paramétricos y aplica las 
    fórmulas normativas (Anexo B.3.3).

    .. math::
        u_{\text{B}71} = \frac{1}{\sqrt{3}} \cdot \max(|\text{deviation}_i|)

    .. math::
        u_{\text{B}72} = 0.5 \cdot \max(U_{xi})

    .. math::
        u_{\text{B}7} = \sqrt{u_{\text{B}71}^2 + u_{\text{B}72}^2}

    Args:
        dataset (List[Dict[str, Any]]): Conjunto de datos recolectados.
        deviation_key (str): Clave del diccionario para las desviaciones 
            calculadas.
        urefs_key (str): Clave del diccionario para las incertidumbres 
            de referencia.

    Returns:
        tuple[float, float, float]: Valores calculados correspondientes 
            a :math:`u_{\text{B}71}`, :math:`u_{\text{B}72}` y la 
            incertidumbre combinada :math:`u_{\text{B}7}`.

    """
    if not dataset:
        return np.nan, np.nan, np.nan

    valid_deviations = [
        np.abs(row[deviation_key]) 
        for row in dataset 
        if not np.isnan(row[deviation_key])
    ]
    valid_urefs = [
        row[urefs_key] 
        for row in dataset 
        if not np.isnan(row[urefs_key])
    ]

    if not valid_deviations or not valid_urefs:
        return np.nan, np.nan, np.nan

    u_B71 = float((1.0 / np.sqrt(3)) * np.nanmax(valid_deviations))
    u_B72 = float(0.5 * np.nanmax(valid_urefs))
    u_B7 = float(np.sqrt(u_B71**2 + u_B72**2))

    return u_B71, u_B72, u_B7

def check_failures(res: Dict[str, float], case: ImpulseCase) -> List[str]:
    r"""Evalúa las métricas calculadas contra los valores de referencia 
    normativos.

    Verifica los parámetros :math:`U_t`, :math:`T_1`, :math:`T_2` y 
    :math:`\text{OS}` comparando los resultados del motor de cálculo con 
    los límites de aceptación de la norma IEC 61083-2. Previo a la 
    evaluación, escala la tensión a :math:`\unit{\kilo\volt}` 
    (dividiendo por :math:`10^3`), y los tiempos a 
    :math:`\unit{\micro\second}` (multiplicando por :math:`10^6`).

    .. note::
        **Motor de Aserciones:** El método aplica distintas tolerancias 
        mediante ``pytest.approx``, conforme lo dicta la normativa:

            - Utiliza tolerancia **relativa** 
              (e.g., ``rel=case.U_tolerance / 100``) para evaluar la 
              tensión pico (:math:`U_t`) y los tiempos de transición 
              (:math:`T_1`, :math:`T_2` o :math:`T_c`).
            - Utiliza tolerancia **absoluta** (``abs=case.OS_tolerance``) 
              exclusivamente para evaluar la magnitud del 
              sobrepasamiento (:math:`\text{OS}`).

    Args:
        res (Dict[str, float]): Diccionario con los parámetros crudos 
            calculados por el analizador, donde la tensión está en 
            :math:`\unit{\volt}` y los tiempos en :math:`\unit{\second}`.
        case (ImpulseCase): Estructura inmutable con los valores de 
            referencia esperados y sus tolerancias.

    Returns:
        List[str]: Lista de cadenas descriptivas con los fallos 
            detectados. Retorna una lista vacía si el análisis converge 
            dentro de las tolerancias normativas.
    """
    # Función auxiliar para validar los parámetros y recolectar fallos.
    failures = []

    # Ut (Peak).
    ut_val = res['Ut'] / 1e3
    ut_ref = case.U_reference
    ut_tol = case.U_tolerance / 100

    if ut_val != pytest.approx(ut_ref, rel=ut_tol):
        msg = (f"-> Peak Error: Esperado {ut_ref}, "
               f"Obtenido {ut_val:.4f}")
        failures.append(msg)

    # T1.
    t1_ref = case.T1_reference
    if not np.isnan(t1_ref):
        t1_val = res['T1'] * 1e6
        t1_tol = case.T1_tolerance / 100

        if t1_val != pytest.approx(t1_ref, rel=t1_tol):
            msg = (f"-> T1 Error: Esperado {t1_ref}, "
                   f"Obtenido {t1_val:.4f}")
            failures.append(msg)

    # T2 / Tc.
    t2_ref = case.T2_reference
    if not np.isnan(t2_ref):
        t2_val = res['T2'] * 1e6
        t2_tol = case.T2_tolerance / 100

        if t2_val != pytest.approx(t2_ref, rel=t2_tol):
            msg = (f"-> T2/Tc Error: Esperado {t2_ref}, "
                   f"Obtenido {t2_val:.4f}")
            failures.append(msg)

    # OS.
    os_ref = case.OS_reference
    if not np.isnan(os_ref):
        os_val = res['OS']
        os_tol = case.OS_tolerance

        if os_val != pytest.approx(os_ref, abs=os_tol):
            msg = (f"-> OS Error: Esperado {os_ref}, "
                   f"Obtenido {os_val:.4f}")
            failures.append(msg)

    return failures

def create_result_dict(
        case: ImpulseCase, 
        uncertainty_case: UncertaintyCase, 
        res: Dict[str, float]
) -> Dict[str, Any]:
    r"""Estructura y formatea las métricas comparativas para su 
    documentación en el reporte PDF.

    Computa las métricas de desviación aplicando escalamiento de unidades:
    - Para tensión y tiempos, calcula la desviación porcentual relativa 
      entre el valor obtenido y la referencia normativa.
    - Para el sobrepasamiento (:math:`\text{OS}`), calcula la desviación 
      aritmética absoluta.

    Args:
        case (ImpulseCase): Caso de prueba instanciado con referencias 
            normativas.
        uncertainty_case (UncertaintyCase): Incertidumbres provistas por 
            la norma para el caso de prueba instanciado (:math:`U_x`).
        res (Dict[str, float]): Resultados paramétricos crudos arrojados 
            por el motor de cálculo matemático.

    Returns:
        Dict[str, Any]: Diccionario que guarda referencias, valores 
            calculados escalados (:math:`\unit{\kilo\volt}` y 
            :math:`\unit{\micro\second}`), desviaciones y las 
            incertidumbres del conjunto de datos.
    """
    u_calc = res['Ut'] / 1e3
    t1_calc = res['T1'] * 1e6
    t2_calc = res['T2'] * 1e6
    os_calc = res['OS']

    u_dev = 100 * (u_calc - case.U_reference) / case.U_reference
    t1_dev = 100 * (t1_calc - case.T1_reference) / case.T1_reference
    t2_dev = 100 * (t2_calc - case.T2_reference) / case.T2_reference
    os_dev = os_calc - case.OS_reference

    return {
        'file_id': case.file_id,
        
        'U_ref': case.U_reference,
        'U_calc': u_calc,
        'U_deviation': u_dev,
        'U_ux': uncertainty_case.U_ux,

        'T1_ref': case.T1_reference,
        'T1_calc': t1_calc,
        'T1_deviation': t1_dev,
        'T1_ux': uncertainty_case.T1_ux,

        'T2_ref': case.T2_reference,
        'T2_calc': t2_calc,
        'T2_deviation': t2_dev,
        'T2_ux': uncertainty_case.T2_ux,

        'OS_ref': case.OS_reference,
        'OS_calc': os_calc,
        'OS_deviation': os_dev,
        'OS_ux': uncertainty_case.OS_ux,
    }

@pytest.fixture(scope="session")
def report_data() -> Generator[Dict[str, Any], None, None]:
    r"""Función de Pytest con alcance de sesión encargada de gestionar 
    el ciclo de vida de los datos de calibración. Inicializa un 
    contenedor centralizado para recolectar las métricas de todas las 
    pruebas ejecutadas y, durante el proceso de desmontaje (*teardown*), 
    dirige la generación del reporte final en formato PDF.

    **Cálculo de Incertidumbres (IEC 61083-2):**
    Si existen datos capturados, evalúa la subrutina ``_calc_uB7``, que 
    resuelve las siguientes ecuaciones estadísticas sobre las 
    desviaciones recolectadas (:math:`\text{deviation}_i`) y las 
    incertidumbres de referencia (:math:`U_{xi}`):

    .. math::
        u_{\text{B}71} = \frac{1}{\sqrt{3}} \cdot \max(|\text{deviation}_i|)

    .. math::
        u_{\text{B}72} = 0.5 \cdot \max(U_{xi})

    .. math::
        u_{\text{B}7} = \sqrt{u_{\text{B}71}^2 + u_{\text{B}72}^2}

    .. note::
        **Fallback de Reporte Vacío:** Si la ejecución de todas las 
        pruebas falla o se omite, las listas quedan vacías. El 
        *teardown* aborta silenciosamente la rutina sin generar un PDF 
        corrupto.

    Yields:
        Dict[str, Any]: Diccionario contenedor de memoria compartida con 
            tres estructuras principales: ``LI`` y ``LIC`` (almacenan 
            los resultados de cada iteración) y ``TDG_META`` (metadatos 
            de cada archivo). Este objeto se inyecta en cada prueba para 
            guardar los cálculos obtenidos.
    """
    # Inicializa y cede el diccionario a las pruebas.
    data = {"LI": [], "LIC": [], "TDG_META": {}}
    yield data # Ejecuta las pruebas.

    # Generar reporte al final del ciclo de vida.
    if not data["LI"] and not data["LIC"]:
        return

    software_meta = {
        "name": __app_name__, 
        "version": __version__, 
        "date": __release_date__, 
        "algorithms": __algorithms_supported__, 
        "parameters": __parameters_validated__
    }

    pdf = ReportPDF(software_meta, data["TDG_META"])
    pdf.add_metadata_section()
    pdf.add_results_table(data["LI"], data["LIC"])

    uncertainty_li = {
        'U': _calc_uB7(data["LI"], 'U_deviation', 'U_ux'),
        'T1': _calc_uB7(data["LI"], 'T1_deviation', 'T1_ux'),
        'T2': _calc_uB7(data["LI"], 'T2_deviation', 'T2_ux'),
        'OS': _calc_uB7(data["LI"], 'OS_deviation', 'OS_ux')
    }

    uncertainty_lic = {
        'U': _calc_uB7(data["LIC"], 'U_deviation', 'U_ux'),
        'T1': _calc_uB7(data["LIC"], 'T1_deviation', 'T1_ux'),
        'T2': _calc_uB7(data["LIC"], 'T2_deviation', 'T2_ux'),
        'OS': _calc_uB7(data["LIC"], 'OS_deviation', 'OS_ux')
    }

    pdf.add_uncertainty_table(uncertainty_li, uncertainty_lic)
    pdf_path = BASE_DIR / "Informe_Calibracion_IEC61083_2.pdf"
    pdf.output(str(pdf_path))
    print(f"\n[+] Informe PDF generado exitosamente en:\n{pdf_path}")

# -----------------------------------------------------------------------------
# PRUEBAS DE IMPULSO PLENO (LI)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "case",
    TEST_CASES_LI,
    ids=lambda c: c.file_id,
)
def test_calibration_iec_li(
    case: ImpulseCase, 
    report_data: Dict[str, Any]
) -> None:
    r"""Ejecuta el conjunto de validación parametrizada para los 
    Impulsos tipo Rayo Plenos (LI).

    Para cada caso de prueba inyectado por Pytest, carga el archivo de 
    datos TDG, inicializa el motor matemático (``LightningImpulseAnalyzer``) 
    y procesa la señal. Posteriormente, compara las métricas resultantes 
    contra los valores de referencia de la norma. Si alguna desviación 
    excede la tolerancia permitida, interrumpe la prueba y reporta un 
    fallo limpio omitiendo la traza de ejecución de Pytest 
    (``pytrace=False``).

    Args:
        case (ImpulseCase): Tupla inyectada por Pytest con los datos del 
            caso de calibración actual.
        report_data (Dict[str, Any]): Diccionario inyectado por el 
            fixture de sesión para guardar los resultados en caso de éxito.
    """
    file_path = BASE_DIR / f"{case.file_id}.txt"
    metadata, data = FileManager.read_TDG_file(file_path)

    if not report_data["TDG_META"]:
        report_data["TDG_META"].update(metadata)

    analyzer = LightningImpulseAnalyzer(
        data, 
        metadata['sampling_period'], 
        1.0
    )
    analyzer.ref_lightning_impulse()

    uncertainty_case = next(
        u for u in UNCERTAINTY_CASES_LI 
        if u.file_id == case.file_id
    )

    result_dict = create_result_dict(
        case, uncertainty_case, analyzer.results
    )
    report_data["LI"].append(result_dict)

    failures = check_failures(analyzer.results, case)
    if failures:
        pytest.fail("\n".join(failures), pytrace=False)

# -----------------------------------------------------------------------------
# PRUEBAS DE IMPULSO CORTADO (LIC)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "case",
    TEST_CASES_LIC,
    ids=lambda c: c.file_id,
)
def test_calibration_iec_lic(
    case: ImpulseCase, 
    report_data: Dict[str, Any]
) -> None:
    r"""Ejecuta el conjunto de validación parametrizada para los 
    Impulsos tipo Rayo Cortados (LIC).

    Implementa el análisis relacional de dos etapas establecido por la 
    norma IEC 61083-2: primero analiza una onda plena de referencia 
    a tensión reducida (archivo sufijo ``f``) para extraer parámetros 
    base; luego, usa este modelo para sincronizar y analizar la onda 
    cortada objetivo (archivo sufijo ``c``).

    .. warning::
        **Omisión Condicionada:** Procesa exclusivamente los impulsos 
        cortados en la cola (``LIC-M4`` y ``LIC-M5``). 
        Para las variantes cortadas en el frente (como ``LIC-A1``), la 
        prueba se omite mediante ``pytest.skip``, ya que su análisis no 
        está implementado.

    Args:
        case (ImpulseCase): Tupla inyectada por Pytest con los datos del 
            caso de calibración actual.
        report_data (Dict[str, Any]): Diccionario inyectado por el 
            fixture de sesión para guardar los resultados en caso de éxito.
    """
    # Verificar si es un caso de corte en la cola (requiere análisis dual).
    if case.file_id in ["LIC-M4", "LIC-M5"]:
        # Cargar y procesar la onda de referencia (f).
        ref_path = BASE_DIR / f"{case.file_id}f.txt"
        ref_metadata, ref_data = FileManager.read_TDG_file(ref_path)
        ref_analyzer = LightningImpulseAnalyzer(
            ref_data, 
            ref_metadata['sampling_period'], 
            1.0
        )
        ref_analyzer.ref_lightning_impulse()

        # Cargar y procesar la onda cortada (c) junto con la referencia.
        chop_path = BASE_DIR / f"{case.file_id}c.txt"
        metadata, data = FileManager.read_TDG_file(chop_path)
        analyzer = LightningImpulseAnalyzer(
            data, 
            metadata['sampling_period'], 
            1.0
        )
        analyzer.lightning_impulse(ref_analyzer)

        uncertainty_case = next(
            u for u in UNCERTAINTY_CASES_LIC 
            if u.file_id == case.file_id
        )

        result_dict = create_result_dict(
            case, uncertainty_case, analyzer.results
        )
        report_data["LIC"].append(result_dict)

        failures = check_failures(analyzer.results, case)
        if failures:
            pytest.fail("\n".join(failures), pytrace=False)
    else:
        # No está implementado el análisis de impulsos cortados en el frente.
        pytest.skip("Pendiente de implementación.")