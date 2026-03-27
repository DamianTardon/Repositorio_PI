import pytest
from pathlib import Path
import numpy as np

# Importar el analizador y sus metadatos.
from impulse_analyzer import LightningImpulseAnalyzer, __app_name__, __version__, __release_date__, __algorithms_supported__, __parameters_validated__
from .test_cases_data import TEST_CASES_LI, UNCERTAINTY_CASES_LI, TEST_CASES_LIC, UNCERTAINTY_CASES_LIC
from report import ReportPDF
from file_manager import FileManager

BASE_DIR = Path(__file__).resolve().parent.parent / 'Calibracion' / 'IEC61083_2'

def check_failures(res, case):
    # Función auxiliar para validar los parámetros y recolectar fallos.
    failures = []

    # Ut (Peak).
    if res['Ut'] / 1e3 != pytest.approx(case.U_reference, rel=case.U_tolerance/100):
        failures.append(f"-> Peak Error: Esperado {case.U_reference}, Obtenido {res['Ut']/1e3:.4f}")

    # T1.
    if not np.isnan(case.T1_reference):
        if res['T1'] * 1e6 != pytest.approx(case.T1_reference, rel=case.T1_tolerance/100):
            failures.append(f"-> T1 Error: Esperado {case.T1_reference}, Obtenido {res['T1']*1e6:.4f}")

    # T2 / Tc.
    if not np.isnan(case.T2_reference):
        if res['T2'] * 1e6 != pytest.approx(case.T2_reference, rel=case.T2_tolerance/100):
            failures.append(f"-> T2/Tc Error: Esperado {case.T2_reference}, Obtenido {res['T2']*1e6:.4f}")

    # OS.
    if not np.isnan(case.OS_reference):
        if res['OS'] != pytest.approx(case.OS_reference, abs=case.OS_tolerance):
            failures.append(f"-> OS Error: Esperado {case.OS_reference}, Obtenido {res['OS']:.4f}")
    return failures

def create_result_dict(case, uncertainty_case, res):
    calc_peak = res['Ut'] / 1e3
    calc_t1 = res['T1'] * 1e6
    calc_t2 = res['T2'] * 1e6
    calc_os = res['OS']

    return {
        'file_id': case.file_id,
        
        'U_ref': case.U_reference, 'U_calc': calc_peak, 
        'U_desv': 100 * (calc_peak - case.U_reference) / case.U_reference, 'U_ux': uncertainty_case.U_ux,
        
        'T1_ref': case.T1_reference, 'T1_calc': calc_t1, 
        'T1_desv': 100 * (calc_t1 - case.T1_reference) / case.T1_reference, 'T1_ux': uncertainty_case.T1_ux,
        
        'T2_ref': case.T2_reference, 'T2_calc': calc_t2, 
        'T2_desv': 100 * (calc_t2 - case.T2_reference) / case.T2_reference, 'T2_ux': uncertainty_case.T2_ux,
        
        'OS_ref': case.OS_reference, 'OS_calc': calc_os, 
        'OS_desv': calc_os - case.OS_reference, 'OS_ux': uncertainty_case.OS_ux,
    }

@pytest.fixture(scope="session")
def report_data():
    # Inicializa y cede el diccionario a los tests.
    data = {"LI": [], "LIC": [], "TDG_META": {}}
    yield data # Ejecuta los test.

    # Generar reporte al final.
    if not data["LI"] and not data["LIC"]:
        return

    software_meta = {
        "name": __app_name__, "version": __version__, "date": __release_date__,
        "algorithms": __algorithms_supported__, "parameters": __parameters_validated__
    }

    pdf = ReportPDF(software_meta, data["TDG_META"])
    pdf.add_metadata_section()
    pdf.add_results_table(data["LI"], data["LIC"])

    # Función auxiliar para calcular Incertidumbres (Anexo B.3.3) de todos los parámetros.
    def calc_uB7(dataset, devs_key, urefs_key):
        if not dataset:
            return np.nan, np.nan, np.nan
        valid_devs = [np.abs(row[devs_key]) for row in dataset if not np.isnan(row[devs_key])]
        valid_urefs = [row[urefs_key] for row in dataset if not np.isnan(row[urefs_key])]
        if not valid_devs or not valid_urefs:
            return np.nan, np.nan, np.nan

        u_B71 = (1.0 / np.sqrt(3)) * np.nanmax(valid_devs)
        u_B72 = 0.5 * np.nanmax(valid_urefs)
        return u_B71, u_B72, np.sqrt(u_B71**2 + u_B72**2)

    uncertainty_li = {
        'U': calc_uB7(data["LI"], 'U_desv', 'U_ux'),
        'T1': calc_uB7(data["LI"], 'T1_desv', 'T1_ux'),
        'T2': calc_uB7(data["LI"], 'T2_desv', 'T2_ux'),
        'OS': calc_uB7(data["LI"], 'OS_desv', 'OS_ux')
    }

    uncertainty_lic = {
        'U': calc_uB7(data["LIC"], 'U_desv', 'U_ux'),
        'T1': calc_uB7(data["LIC"], 'T1_desv', 'T1_ux'),
        'T2': calc_uB7(data["LIC"], 'T2_desv', 'T2_ux'),
        'OS': calc_uB7(data["LIC"], 'OS_desv', 'OS_ux')
    }

    pdf.add_uncertainty_table(uncertainty_li, uncertainty_lic)
    pdf_path = BASE_DIR / "Informe_Calibracion_IEC61083_2.pdf"
    pdf.output(str(pdf_path))
    print(f"\n[+] Informe PDF generado exitosamente en:\n{pdf_path}")


# -----------------------------------------------------------------------------------------
# TESTS DE IMPULSO COMPLETO (LI)
# -----------------------------------------------------------------------------------------
@pytest.mark.parametrize("case", TEST_CASES_LI, ids=[c.file_id for c in TEST_CASES_LI])
def test_calibration_iec_li(case, report_data):
    file_path = BASE_DIR / f"{case.file_id}.txt"
    metadata, data = FileManager.read_TDG_file(file_path)

    if not report_data["TDG_META"]:
        report_data["TDG_META"].update(metadata)

    analyzer = LightningImpulseAnalyzer(data, metadata['sampling_period'], 1.0)
    analyzer.ref_lightning_impulse()

    uncertainty_case = next(u for u in UNCERTAINTY_CASES_LI if u.file_id == case.file_id)
    report_data["LI"].append(create_result_dict(case, uncertainty_case, analyzer.results))

    failures = check_failures(analyzer.results, case)
    if failures:
        pytest.fail("\n".join(failures), pytrace=False)

# -----------------------------------------------------------------------------------------
# TESTS DE IMPULSO CORTADO (LIC)
# -----------------------------------------------------------------------------------------
@pytest.mark.parametrize("case", TEST_CASES_LIC, ids=[c.file_id for c in TEST_CASES_LIC])
def test_calibration_iec_lic(case, report_data):
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

        uncertainty_case = next(u for u in UNCERTAINTY_CASES_LIC if u.file_id == case.file_id)
        report_data["LIC"].append(create_result_dict(case, uncertainty_case, analyzer.results))

        failures = check_failures(analyzer.results, case)
        if failures:
            pytest.fail("\n".join(failures), pytrace=False)
    else:
        # Los casos LIC-A1, LIC-M1, LIC-M2, LIC-M3 no se analizan por el momento.
        pytest.skip("Pendiente de implementación.")