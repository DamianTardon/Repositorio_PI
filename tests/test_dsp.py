import pytest
import numpy as np
from src.dsp import LightningImpulseAnalyzer

# --- Configuración de datos iniciales ---

@pytest.fixture
def impulse_params():
    """
    Devuelve los parámetros teóricos para generar una onda 1.2/50 µs.
    """
    return {
        'U': 10000.0,       # 10 kV
        'tau1': 68.2e-6,    # Constante de tiempo de cola
        'tau2': 0.405e-6,   # Constante de tiempo de frente
        'td': 5e-6,         # Retardo de inicio
        'sample_rate': 100e6, # 100 MS/s
        'duration': 100e-6  # 100 µs
    }

@pytest.fixture
def synthetic_wave(impulse_params):
    """
    Genera una onda doble exponencial limpia basada en los parámetros.
    Devuelve un diccionario con el eje de tiempo y voltaje.
    """
    t = np.arange(0, impulse_params['duration'], 1/impulse_params['sample_rate'])
    dt = t - impulse_params['td']
    
    # Máscara para simular que antes de td el voltaje es 0
    mask = dt >= 0
    voltage = np.zeros_like(t)
    
    # Fórmula doble exponencial: U * (exp(-t/tau1) - exp(-t/tau2))
    term1 = np.exp(-dt[mask] / impulse_params['tau1'])
    term2 = np.exp(-dt[mask] / impulse_params['tau2'])
    voltage[mask] = impulse_params['U'] * (term1 - term2)
    
    return {'time': t, 'voltage': voltage, 'rate': impulse_params['sample_rate']}

# --- Tests Unitarios ---

def test_full_process_clean_signal(synthetic_wave):
    """
    Verifica que el flujo completo calcule T1=1.2us y T2=50us 
    con una señal ideal.
    """
    analyzer = LightningImpulseAnalyzer(synthetic_wave['voltage'], 1/synthetic_wave['rate'])
    
    # Ejecutar pipeline completo
    analyzer.remove_offset()
    analyzer.normalize_waveform()
    analyzer.cutting_signal()
    analyzer.fit_base_curve()
    analyzer.construct_base_curve()
    analyzer.calculate_residual_curve()
    analyzer.filter_to_residual()
    analyzer.construct_test_voltage_curve()
    results = analyzer.calculate_parameters()
    
    # Validaciones con pytest.approx para punto flotante
    # T1 esperado ~ 1.2 µs (Tolerancia absoluta 0.1 µs)
    assert results['T1'] * 1e6 == pytest.approx(1.2, abs=0.1)
    
    # T2 esperado ~ 50 µs (Tolerancia absoluta 2 µs)
    assert results['T2'] * 1e6 == pytest.approx(50.0, abs=2.0)
    
    # Ut debe ser cercano al pico teórico
    expected_peak = np.max(synthetic_wave['voltage'])
    assert results['Ut'] == pytest.approx(expected_peak, rel=0.01) # 1% error relativo

def test_offset_removal(synthetic_wave):
    """
    Verifica que el sistema elimine correctamente un offset DC positivo.
    """
    offset_val = 500.0
    dirty_voltage = synthetic_wave['voltage'] + offset_val
    
    analyzer = LightningImpulseAnalyzer(dirty_voltage, synthetic_wave['rate'])
    calculated_offset = analyzer.remove_offset(pre_trigger_percent=5)
    
    assert calculated_offset == pytest.approx(offset_val, abs=1.0)
    
    # Verificar que el pre-trigger vuelva a ser cero
    # Tomamos las primeras 10 muestras para asegurar
    assert np.mean(analyzer.zeroed_voltage[:10]) == pytest.approx(0.0, abs=0.1)

def test_polarity_negative(synthetic_wave):
    """
    Verifica que el sistema detecte y normalice impulsos negativos.
    """
    neg_voltage = synthetic_wave['voltage'] * -1.0
    
    analyzer = LightningImpulseAnalyzer(neg_voltage, synthetic_wave['rate'])
    analyzer.remove_offset()
    peak, polarity = analyzer.normalize_waveform()
    
    assert polarity == "Negativa"
    assert peak > 0  # El pico debe ser positivo internamente tras normalizar
    assert analyzer.factor == -1.0

def test_curve_fit_parameters(synthetic_wave, impulse_params):
    """
    Verifica si el algoritmo Levenberg-Marquardt recupera las constantes
    de tiempo originales (tau1 y tau2).
    """
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
    """
    Verifica que el cálculo converja incluso con ruido blanco añadido.
    """
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
    """
    Verifica que lance ValueError si no hay suficientes datos para el offset.
    """
    short_data = np.zeros(10) # Muy pocos datos
    analyzer = LightningImpulseAnalyzer(short_data, 100e6)
    
    with pytest.raises(ValueError, match="No hay suficientes muestras"):
        analyzer.remove_offset(pre_trigger_percent=50)

def test_signal_too_low():
    """
    Verifica el error cuando la señal no cumple los umbrales de recorte (ej. señal plana).
    """
    flat_data = np.zeros(1000)
    analyzer = LightningImpulseAnalyzer(flat_data, 100e6)
    analyzer.remove_offset()
    analyzer.normalize_waveform()
    
    # Debería fallar en cutting_signal porque nunca cruza el 20% del "pico" (que es 0)
    # O el argmax devuelve 0.
    with pytest.raises(ValueError):
        analyzer.cutting_signal()