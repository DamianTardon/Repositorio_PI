import pytest
from pathlib import Path
import math
from procesador_de_senales_2 import LightningImpulseAnalyzer
from .test_cases_data import TEST_CASES

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

@pytest.mark.parametrize("case", TEST_CASES, ids=[c.file_id for c in TEST_CASES])
def test_calibration_files_iec(case):
    # 1. Cargar datos:
    data, rate = load_tdg_wave_file(case.file_id)
    sigma_fit = 1.0
    analyzer = LightningImpulseAnalyzer(data, rate, sigma_fit)
    
    # 2. Procesar datos:
    analyzer.full_lightning_impulses()
    
    # 3. Validar resultados mediante recolección de fallos:
    res = analyzer.results
    failures = []

    # Ut
    if res['Ut'] / 1e3 != pytest.approx(case.expected_peak, rel=case.tolerance_peak/100):
        failures.append(
            f"-> Peak Error: Esperado {case.expected_peak}, Obtenido {res['Ut']/1e3:.4f}"
        )

    # T1
    if not math.isnan(case.expected_T1):
        if res['T1'] * 1e6 != pytest.approx(case.expected_T1, rel=case.tolerance_T1/100):
            failures.append(
                f"-> T1 Error: Esperado {case.expected_T1}, Obtenido {res['T1']*1e6:.4f}"
            )

    # T2
    if res['T2'] * 1e6 != pytest.approx(case.expected_T2, rel=case.tolerance_T2/100):
        failures.append(
            f"-> T2 Error: Esperado {case.expected_T2}, Obtenido {res['T2']*1e6:.4f}"
        )

    # Beta
    if not math.isnan(case.expected_beta):
        if res['Beta_prime'] != pytest.approx(case.expected_beta, abs=case.tolerance_beta):
            failures.append(
                f"-> Beta Error: Esperado {case.expected_beta}, Obtenido {res['Beta_prime']:.4f}"
            )

    # Reporte de errores completo:
    #assert not failures, "\n".join(failures)
    if failures:
        # pytrace=False oculta el código fuente en el error, dejando solo el mensaje.
        pytest.fail("\n".join(failures), pytrace=False)