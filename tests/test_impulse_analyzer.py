import pytest
from pathlib import Path
import math
from impulse_analyzer import LightningImpulseAnalyzer
from .test_cases_data import TEST_CASES_LI, TEST_CASES_LIC

BASE_DIR = Path(__file__).resolve().parent.parent / 'Calibracion' / 'IEC61083_2'

def load_tdg_wave_file(filename: str):
    file_path = BASE_DIR / filename
    metadata = {}
    data = []

    with open(file_path, 'r') as f:
        metadata['software_version'] = f.readline().strip()
        metadata['version_file'] = f.readline().strip()
        metadata['wave_name'] = f.readline().strip()
        line_4 = f.readline().strip()
        resolution_samples_time = line_4.split(',')
        metadata['resolution'] = resolution_samples_time[0].strip()
        samples_time = resolution_samples_time[1].strip().split(' samples at ')
        metadata['samples'] = int(samples_time[0])
        metadata['interval'] = samples_time[1].strip()

        metadata['rate'] = float(f.readline().strip())

        for line in f:
            if line.strip():
                data.append(float(line.strip()))
                
    return data, metadata['rate']

def check_failures(res, case):
    # Función auxiliar para validar los parámetros y recolectar fallos.
    failures = []
    
    # Ut (Peak)
    if res['Ut'] / 1e3 != pytest.approx(case.expected_peak, rel=case.tolerance_peak/100):
        failures.append(f"-> Peak Error: Esperado {case.expected_peak}, Obtenido {res['Ut']/1e3:.4f}")

    # T1
    if not math.isnan(case.expected_T1):
        if res['T1'] * 1e6 != pytest.approx(case.expected_T1, rel=case.tolerance_T1/100):
            failures.append(f"-> T1 Error: Esperado {case.expected_T1}, Obtenido {res['T1']*1e6:.4f}")

    # T2 / Tc
    if res['T2'] * 1e6 != pytest.approx(case.expected_T2, rel=case.tolerance_T2/100):
        failures.append(f"-> T2/Tc Error: Esperado {case.expected_T2}, Obtenido {res['T2']*1e6:.4f}")

    # Beta
    if not math.isnan(case.expected_beta):
        if res['Beta_prime'] != pytest.approx(case.expected_beta, abs=case.tolerance_beta):
            failures.append(f"-> Beta Error: Esperado {case.expected_beta}, Obtenido {res['Beta_prime']:.4f}")
            
    return failures

# -----------------------------------------------------------------------------------------
# TESTS DE IMPULSO COMPLETO (LI)
# -----------------------------------------------------------------------------------------
@pytest.mark.parametrize("case", TEST_CASES_LI, ids=[c.file_id for c in TEST_CASES_LI])
def test_calibration_iec_li(case):
    # Cargar y procesar la onda con la función para impulsos completos.
    data, rate = load_tdg_wave_file(f"{case.file_id}.txt")
    analyzer = LightningImpulseAnalyzer(data, rate, 1.0)
    analyzer.ref_lightning_impulse()

    failures = check_failures(analyzer.results, case)
    if failures:
        pytest.fail("\n".join(failures), pytrace=False)

# -----------------------------------------------------------------------------------------
# TESTS DE IMPULSO CORTADO (LIC)
# -----------------------------------------------------------------------------------------
@pytest.mark.parametrize("case", TEST_CASES_LIC, ids=[c.file_id for c in TEST_CASES_LIC])
def test_calibration_iec_lic(case):
    # Verificar si es un caso de corte en la cola (requiere análisis dual)
    if case.file_id in ["LIC-M4", "LIC-M5"]:
        # 1. Cargar y procesar la onda de referencia (f)
        ref_data, ref_rate = load_tdg_wave_file(f"{case.file_id}f.txt")
        ref_analyzer = LightningImpulseAnalyzer(ref_data, ref_rate, 1.0)
        ref_analyzer.ref_lightning_impulse()

        # 2. Cargar y procesar la onda cortada (c) junto con la referencia.
        data, rate = load_tdg_wave_file(f"{case.file_id}c.txt")
        analyzer = LightningImpulseAnalyzer(data, rate, 1.0)
        analyzer.lightning_impulse(ref_analyzer)

        failures = check_failures(analyzer.results, case)
        if failures:
            pytest.fail("\n".join(failures), pytrace=False)
            
    else:
        # Los casos LIC-A1, LIC-M1, LIC-M2, LIC-M3 no se analizan por el momento.
        pytest.skip("Pendiente de implementación.")