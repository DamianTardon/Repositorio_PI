import pytest
from pathlib import Path
import numpy as np
from src.procesador_de_senales import LightningImpulseAnalyzer

# --- Carga de datos de calibración ---

@pytest.fixture
def data_calibration():
    """
    Extrae los parámetros del archivo generado por el IEC61083-2 Test Data Generator,
    para generar una onda de impulso.
    """
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
def test_cutting_signal(synthetic_wave):
    signal = [1,2,3,4,5,6,7,8,9,10]
    rate = 1e6
    analyzer = LightningImpulseAnalyzer(signal, rate)
    analyzer._remove_offset()
    analyzer._normalize_waveform()
    analyzer._cutting_signal()
"""

"""
def test_curve_fit_parameters(synthetic_wave, impulse_params):

    # Verifica si el algoritmo Levenberg-Marquardt recupera las constantes
    # de tiempo originales (tau1 y tau2).

    analyzer = LightningImpulseAnalyzer(synthetic_wave['voltage'], synthetic_wave['rate'])
    analyzer.remove_offset()
    analyzer.normalize_waveform()
    analyzer.cutting_signal()
    analyzer.fit_base_curve()
    
    params = analyzer.fitted_params
    
    # Tolerancia del 5% debido al recorte de señal (cutting_signal)
    assert params['tau1'] == pytest.approx(impulse_params['tau1'], rel=0.05)
    assert params['tau2'] == pytest.approx(impulse_params['tau2'], rel=0.05)

def test_noise_robustness(synthetic_wave):

    # Verifica que el cálculo converja incluso con ruido blanco añadido.

    np.random.seed(42)
    noise = np.random.normal(0, 50, len(synthetic_wave['voltage'])) # Ruido sigma=50V
    noisy_voltage = synthetic_wave['voltage'] + noise
    
    analyzer = LightningImpulseAnalyzer(noisy_voltage, synthetic_wave['rate'])
    
    # Ejecutamos pasos manuales para asegurar que no salte excepción en el fit
    analyzer.remove_offset()
    analyzer.normalize_waveform()
    analyzer.cutting_signal()
    analyzer.fit_base_curve()
    analyzer.construct_base_curve()
    analyzer.calculate_residual_curve()
    analyzer.filter_to_residual()
    analyzer.construct_test_voltage_curve()
    res = analyzer.calculate_parameters()
    
    # A pesar del ruido, los tiempos T1 y T2 deben mantenerse razonables
    assert res['T1']*1e6 == pytest.approx(1.2, abs=0.2)
    assert res['T2']*1e6 == pytest.approx(50.0, abs=3.0)

def test_insufficient_pretrigger():

    # Verifica que lance ValueError si no hay suficientes datos para el offset.

    short_data = np.zeros(10) # Muy pocos datos
    analyzer = LightningImpulseAnalyzer(short_data, 100e6)
    
    with pytest.raises(ValueError, match="No hay suficientes muestras"):
        analyzer.remove_offset(pre_trigger_percent=50)

def test_signal_too_low():

    # Verifica el error cuando la señal no cumple los umbrales de recorte (ej. señal plana).

    flat_data = np.zeros(1000)
    analyzer = LightningImpulseAnalyzer(flat_data, 100e6)
    analyzer.remove_offset()
    analyzer.normalize_waveform()
    
    # Debería fallar en cutting_signal porque nunca cruza el 20% del "pico" (que es 0)
    # O el argmax devuelve 0.
    with pytest.raises(ValueError):
        analyzer.cutting_signal()

    """