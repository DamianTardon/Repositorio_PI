import pytest
from pathlib import Path
import numpy as np

# Importar el analizador y sus metadatos.
from impulse_analyzer import LightningImpulseAnalyzer, __app_name__, __version__, __release_date__, __algorithms_supported__, __parameters_validated__
from .test_cases_data import TEST_CASES_LI, UNCERTAINTY_CASES_LI, TEST_CASES_LIC, UNCERTAINTY_CASES_LIC
from report import ReportPDF
from file_manager import FileManager

BASE_DIR = Path(__file__).resolve().parent.parent / 'Calibracion' / 'IEC61083_2'

# Estructuras globales para guardar los resultados y la metadata para el reporte.
SESSION_RESULTS_LI = []
GLOBAL_TDG_META = {}

def check_failures(res, case):
    # Función auxiliar para validar los parámetros y recolectar fallos.
    failures = []

    # Ut (Peak).
    if res['Ut'] / 1e3 != pytest.approx(case.expected_peak, rel=case.tolerance_peak/100):
        failures.append(f"-> Peak Error: Esperado {case.expected_peak}, Obtenido {res['Ut']/1e3:.4f}")

    # T1.
    if not np.isnan(case.expected_T1):
        if res['T1'] * 1e6 != pytest.approx(case.expected_T1, rel=case.tolerance_T1/100):
            failures.append(f"-> T1 Error: Esperado {case.expected_T1}, Obtenido {res['T1']*1e6:.4f}")

    # T2 / Tc.
    if not np.isnan(case.expected_T2):
        if res['T2'] * 1e6 != pytest.approx(case.expected_T2, rel=case.tolerance_T2/100):
            failures.append(f"-> T2/Tc Error: Esperado {case.expected_T2}, Obtenido {res['T2']*1e6:.4f}")

    # Beta.
    if not np.isnan(case.expected_beta):
        if res['Beta_prime'] != pytest.approx(case.expected_beta, abs=case.tolerance_beta):
            failures.append(f"-> Beta Error: Esperado {case.expected_beta}, Obtenido {res['Beta_prime']:.4f}")
            
    return failures

@pytest.fixture(scope="session", autouse=True)
def pdf_report_generator():
    global SESSION_RESULTS_LI, GLOBAL_TDG_META
    SESSION_RESULTS_LI = []

    yield # Aquí corren todos los tests.

    if not SESSION_RESULTS_LI:
        return

    software_meta = {
        "name": __app_name__, "version": __version__, "date": __release_date__,
        "algorithms": __algorithms_supported__, "parameters": __parameters_validated__
    }

    pdf = ReportPDF(software_meta, GLOBAL_TDG_META)
    pdf.add_metadata_section()
    pdf.add_results_table(SESSION_RESULTS_LI)

    # Función auxiliar para calcular Incertidumbres (Anexo B.3.3) de todos los parámetros.
    def calc_uB7(devs_key, urefs_key):
        # Extraer listas absolutas ignorando NaNs.
        valid_devs = [np.abs(row[devs_key]) for row in SESSION_RESULTS_LI if not np.isnan(row[devs_key])]
        valid_urefs = [row[urefs_key] for row in SESSION_RESULTS_LI if not np.isnan(row[urefs_key])]

        if not valid_devs or not valid_urefs:
            return np.nan, np.nan, np.nan

        max_dev = np.nanmax(valid_devs)
        max_uref = np.nanmax(valid_urefs)

        u_B71 = (1.0 / np.sqrt(3)) * max_dev
        u_B72 = 0.5 * max_uref
        u_B7 = np.sqrt(u_B71**2 + u_B72**2)
        return u_B71, u_B72, u_B7

    unc_results = {}
    unc_results['Ut'] = calc_uB7('dev_peak', 'u_ref_peak')
    unc_results['T1'] = calc_uB7('dev_t1', 'u_ref_t1')
    unc_results['T2'] = calc_uB7('dev_t2', 'u_ref_t2')
    unc_results['Beta'] = calc_uB7('dev_beta', 'u_ref_beta')

    pdf.add_uncertainty_calculations(unc_results)

    # Guardar archivo.
    pdf.output("Informe_Calibracion_IEC61083_2.pdf")
    print("\n[+] Informe PDF generado exitosamente.")

# -----------------------------------------------------------------------------------------
# TESTS DE IMPULSO COMPLETO (LI)
# -----------------------------------------------------------------------------------------
@pytest.mark.parametrize("case", TEST_CASES_LI, ids=[c.file_id for c in TEST_CASES_LI])
def test_calibration_iec_li(case):
    # Cargar y procesar la onda con la función para impulsos completos.
    global GLOBAL_TDG_META

    # Leer el archivo de la onda.
    file_path = BASE_DIR / f"{case.file_id}.txt"
    metadata, data = FileManager.read_TDG_file(file_path)

    if not GLOBAL_TDG_META:
        GLOBAL_TDG_META = metadata

    analyzer = LightningImpulseAnalyzer(data, metadata['sampling_period'], 1.0)
    analyzer.ref_lightning_impulse()
    res = analyzer.results

    # Buscar el caso de incertidumbre correspondiente en UNCERTAINTY_CASES_LI.
    unc_case = next(u for u in UNCERTAINTY_CASES_LI if u.file_id == case.file_id)

    # Calcular Desviaciones.
    calc_peak = res['Ut'] / 1e3
    dev_peak = 100 * (calc_peak - case.expected_peak) / case.expected_peak

    calc_t1 = res['T1'] * 1e6
    dev_t1 = 100 * (calc_t1 - case.expected_T1) / case.expected_T1

    calc_t2 = res['T2'] * 1e6
    dev_t2 = 100 * (calc_t2 - case.expected_T2) / case.expected_T2

    calc_beta = res['Beta_prime']
    dev_beta = calc_beta - case.expected_beta # Error absoluto para Beta'.

    # Guardar en memoria para el reporte en PDF.
    SESSION_RESULTS_LI.append({
        'file_id': case.file_id,
        'ref_peak': case.expected_peak, 'calc_peak': calc_peak, 'dev_peak': dev_peak, 'u_ref_peak': unc_case.U_ux_pct,
        'ref_t1': case.expected_T1, 'calc_t1': calc_t1, 'dev_t1': dev_t1, 'u_ref_t1': unc_case.T1_ux_pct,
        'ref_t2': case.expected_T2, 'calc_t2': calc_t2, 'dev_t2': dev_t2, 'u_ref_t2': unc_case.T2_ux_pct,
        'ref_beta': case.expected_beta, 'calc_beta': calc_beta, 'dev_beta': dev_beta, 'u_ref_beta': unc_case.beta_ux_abs,
    })

    failures = check_failures(res, case)
    if failures:
        pytest.fail("\n".join(failures), pytrace=False)

# -----------------------------------------------------------------------------------------
# TESTS DE IMPULSO CORTADO (LIC)
# -----------------------------------------------------------------------------------------
@pytest.mark.parametrize("case", TEST_CASES_LIC, ids=[c.file_id for c in TEST_CASES_LIC])
def test_calibration_iec_lic(case):
    # Verificar si es un caso de corte en la cola (requiere análisis dual).
    if case.file_id in ["LIC-M4", "LIC-M5"]:
        # Cargar y procesar la onda de referencia (f).
        ref_path = BASE_DIR / f"{case.file_id}f.txt"
        ref_metadata, ref_data = FileManager.read_TDG_file(ref_path)
        ref_analyzer = LightningImpulseAnalyzer(ref_data, ref_metadata['sampling_period'], 1.0)
        ref_analyzer.ref_lightning_impulse()

        # Cargar y procesar la onda cortada (c) junto con la referencia.
        chop_path = BASE_DIR / f"{case.file_id}c.txt"
        metadata, data = FileManager.read_TDG_file(chop_path)
        analyzer = LightningImpulseAnalyzer(data, metadata['sampling_period'], 1.0)
        analyzer.lightning_impulse(ref_analyzer)

        failures = check_failures(analyzer.results, case)
        if failures:
            pytest.fail("\n".join(failures), pytrace=False)

    else:
        # Los casos LIC-A1, LIC-M1, LIC-M2, LIC-M3 no se analizan por el momento.
        pytest.skip("Pendiente de implementación.")