import pytest
from pathlib import Path
#import numpy as np
import math
from src.procesador_de_senales import LightningImpulseAnalyzer
from .test_cases_data import TEST_CASES

BASE_DIR = Path(__file__).resolve().parent.parent / 'src' / 'ArchivosCalibracion'

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
    analyzer = LightningImpulseAnalyzer(data, rate)
    
    # 2. Procesar datos:
    analyzer.signal_processing()
    
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

#---------------------------------------------------------------------------------------------------------------------
"""
# --- Carga de datos de calibración ---

@pytest.fixture
def data_calibration():
    
    #Extrae los parámetros del archivo generado por el IEC61083-2 Test Data Generator,
    #para generar una onda de impulso.
    
    calibration_file = Path(__file__).resolve().parent.parent / 'src' / 'ArchivosCalibracion' / 'LI-A1.txt'

    metadata = {}
    data = []
    
    with open(calibration_file, 'r') as f:
        
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
                data.append(int(line.strip()))

    return data, metadata['rate']

# --- Tests Unitarios ---

def test_full_process_signal(data_calibration):
    data, rate = data_calibration
    analyzer = LightningImpulseAnalyzer(data, rate)
    
    # Ejecutar pipeline completo.
    analyzer.signal_processing()
    
    # Validaciones:
    expected_peak = 1049.6
    expected_T1 = 0.840
    expected_T2 = 60.16
    expected_beta = 0.0

    assert analyzer.results['Ut'] / 1e3 == pytest.approx(expected_peak, rel=0.001)
    assert analyzer.results['T1'] * 1e6 == pytest.approx(expected_T1, rel=2.0)
    assert analyzer.results['T2'] * 1e6 == pytest.approx(expected_T2, rel=0.01)
    assert analyzer.results['Beta_prime'] == pytest.approx(expected_beta, abs=1.0)

def test_peak_value(data_calibration):
    data, rate = data_calibration
    analyzer = LightningImpulseAnalyzer(data, rate)

    analyzer.signal_processing()
    expected_peak = 1049.6

    assert analyzer.results['Ut'] / 1e3 == pytest.approx(expected_peak, rel=0.001)

def test_T1_value(data_calibration):
    data, rate = data_calibration
    analyzer = LightningImpulseAnalyzer(data, rate)

    analyzer.signal_processing()
    expected_T1 = 0.840

    assert analyzer.results['T1'] * 1e6 == pytest.approx(expected_T1, rel=2.0)

def test_T2_value(data_calibration):
    data, rate = data_calibration
    analyzer = LightningImpulseAnalyzer(data, rate)

    analyzer.signal_processing()
    expected_T2 = 60.16

    assert analyzer.results['T2'] * 1e6 == pytest.approx(expected_T2, rel=0.01)

def test_beta_value(data_calibration):
    data, rate = data_calibration
    analyzer = LightningImpulseAnalyzer(data, rate)

    analyzer.signal_processing()
    expected_beta = 0.0

    assert analyzer.results['Beta_prime'] == pytest.approx(expected_beta, abs=1.0)

def test_waveform_iec60060_1(data_calibration):
    data, rate = data_calibration
    analyzer = LightningImpulseAnalyzer(data, rate)
    analyzer.signal_processing()

    # Validaciones:
    expected_T1 = 1.2
    expected_T2 = 50.0

    assert analyzer.results['T1'] * 1e6 == pytest.approx(expected_T1, rel=0.3)
    assert analyzer.results['T2'] * 1e6 == pytest.approx(expected_T2, rel=0.2)


#---------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def synthetic_wave():
    time_axis = np.arange(4000) * 10e-9
    voltage = np.sin(2 * np.pi *1e6 * time_axis)

    return {"voltage": voltage, "rate": 10e9}

def test_offset_removal_positive(synthetic_wave):
    offset_val = 500.0
    signal = synthetic_wave['voltage'] + offset_val

    analyzer = LightningImpulseAnalyzer(signal, synthetic_wave['rate'])
    analyzer._remove_offset()

    assert analyzer.offset_value == pytest.approx(offset_val, rel=1)
    assert np.mean(analyzer.zeroed_curve[:10]) == pytest.approx(0.0, abs=1)

def test_offset_removal_negative(synthetic_wave):
    offset_val = -500.0
    signal = synthetic_wave['voltage'] + offset_val

    analyzer = LightningImpulseAnalyzer(signal, synthetic_wave['rate'])
    analyzer._remove_offset()

    assert analyzer.offset_value == pytest.approx(offset_val, rel=1)
    assert np.mean(analyzer.zeroed_curve[:10]) == pytest.approx(0.0, abs=1)

def test_polarity_positive(synthetic_wave):
    signal = synthetic_wave['voltage'] + 500.0
    analyzer = LightningImpulseAnalyzer(signal, synthetic_wave['rate'])
    analyzer._remove_offset()
    analyzer._normalize_waveform()

    assert analyzer.peak_value > 0
    assert analyzer.polarity == "Positiva"
    assert analyzer.factor == 1.0

def test_polarity_not_positive(synthetic_wave):
    signal = (synthetic_wave['voltage'] + 500.0) * -1.0
    analyzer = LightningImpulseAnalyzer(signal, synthetic_wave['rate'])
    analyzer._remove_offset()
    analyzer._normalize_waveform()

    assert analyzer.peak_value > 0
    assert not analyzer.polarity == "Positiva"
    assert not analyzer.factor == 1.0

def test_polarity_negative(synthetic_wave):
    signal = (synthetic_wave['voltage'] - 500.0) * -1.0
    analyzer = LightningImpulseAnalyzer(signal, synthetic_wave['rate'])
    analyzer._remove_offset()
    analyzer._normalize_waveform()

    assert analyzer.peak_value > 0
    assert analyzer.polarity == "Negativa"
    assert analyzer.factor == -1.0

def test_polarity_not_negative(synthetic_wave):
    signal = synthetic_wave['voltage'] - 500.0
    analyzer = LightningImpulseAnalyzer(signal, synthetic_wave['rate'])
    analyzer._remove_offset()
    analyzer._normalize_waveform()

    assert analyzer.peak_value > 0
    assert not analyzer.polarity == "Negativa"
    assert not analyzer.factor == -1.0
"""