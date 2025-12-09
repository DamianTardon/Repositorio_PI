import numpy as np
from scipy.optimize import curve_fit

class LightningImpulseAnalyzer:
    def __init__(self, voltage_data, sample_rate):
        # Datos de entrada:
        self.raw_voltage = np.array(voltage_data)
        self.sample_rate = sample_rate
        
        # Generar array de tiempo automáticamente: t = index * intervalo
        self.time_axis = np.arange(len(self.raw_voltage)) * self.sample_rate
        
        # Variables de estado:
        self.zeroed_voltage = None
        self.offset_value = 0.0
        
        # Parámetros calculados:
        self.peak_value = 0.0
        self.polarity = None
        self.idx_peak = None
        self.norm_voltage = None
        self.factor = 1.0
        self.start_slice = None
        self.end_slice = None
        self.fit_voltage = None
        self.fit_time = None

    def remove_offset(self, pre_trigger_percent=10):
        # a) Encontrar el nivel de base de la curva registrada.
        # 1. Calcular cantidad de muestras de ruido de fondo.
        total_samples = len(self.raw_voltage)
        n_samples_background = int(total_samples * (pre_trigger_percent / 100))
        
        if n_samples_background < 1:
            raise ValueError("No hay suficientes muestras de pre-trigger para calcular el offset.")

        # 2. Calcular el promedio del ruido (Offset).
        background_noise = self.raw_voltage[:n_samples_background]
        self.offset_value = np.mean(background_noise)
        
        # b) Eliminar el offset de la curva registrada.
        # 1. Restar el offset a toda la señal.
        self.zeroed_voltage = self.raw_voltage - self.offset_value
        
        return self.offset_value
    
    def normalize_waveform(self):
        # 1. Encontrar el índice del máximo valor absoluto.
        self.idx_peak = np.argmax(np.abs(self.zeroed_voltage))
        original_peak = self.zeroed_voltage[self.idx_peak]
        
        # 2. Obtener el valor real de voltaje (Ue) en ese punto.
        self.peak_value = self.zeroed_voltage[self.idx_peak]
        
        # 3. Determinar la polaridad de la señal.
        if original_peak >= 0:
            self.polarity = "Positiva"
            self.factor = 1.0
        else:
            self.polarity = "Negativa"
            self.factor = -1.0
        
        # Invertir polaridad si es negativa.
        self.zeroed_voltage = self.zeroed_voltage * self.factor
        self.peak_value = original_peak * self.factor

        # 4. Normalizar la señal.
        self.norm_voltage = self.zeroed_voltage / self.peak_value
        
        return self.peak_value, self.polarity
    
    def data_for_fitting(self):
        tension = self.zeroed_voltage
        front_data = tension[:self.idx_peak]
        tail_data = tension[self.idx_peak:]
        U_e = self.peak_value
        threshold_20 = 0.2 * U_e
        threshold_40 = 0.4 * U_e

        # d) Encontrar la última muestra en el frente inferior a 0,2 * Ue.
        # 1. Invertir el array del frente para buscar desde el pico hacia atrás.
        front_reversed = front_data[::-1]
        # 2. Buscar el primer punto menor que umbral.
        idx_20_reversed = np.argmax(front_reversed < threshold_20)
        
        # Verificación:
        # Si argmax devuelve 0, puede ser que lo encontró en el índice 0 o que no encontró nada.
        if idx_20_reversed == 0 and front_reversed[0] >= threshold_20:
             raise ValueError("Error: No se encontraron datos < 0.2*Ue")

        # 3. Convertir el índice invertido al índice global.
        idx_20 = (len(front_data) - 1) - idx_20_reversed

        # e) Encontrar la última muestra en la cola superior a 0,4 * Ue.
        # 1. Buscar el primer punto menor que umbral.
        idx_40_under = np.argmax(tail_data < threshold_40)

        # Verificación:
        # Si devuelve 0, puede ser que la señal no cumple valor < 0.4 * Ue.
        if idx_40_under == 0:
            raise ValueError("Error: La señal no cae por debajo de 0.4*Ue en la cola.")

        # 2. Ajustar al índice global.
        idx_40 = self.idx_peak + idx_40_under

        # f) Seleccionar datos entre el 20 % y el 40 % para el ajuste.
        # Limite inferior:
        self.start_slice = idx_20 + 1
        # Limite superior:
        self.end_slice = idx_40 + 1
        # Guardar los datos recortados para el ajuste
        self.fit_voltage = self.zeroed_voltage[self.start_slice:self.end_slice]
        self.fit_voltage_normalized = self.norm_voltage[self.start_slice:self.end_slice]
        self.fit_time = self.time_axis[self.start_slice:self.end_slice]
        
        print(f"Pico={self.peak_value}")
        print(f"20% umbral= {threshold_20}, ID={self.start_slice}, V={self.zeroed_voltage[self.start_slice]}")
        print(f"40% umbral= {threshold_40}, ID={self.end_slice}, V={self.zeroed_voltage[self.end_slice]}")

        return self.fit_time, self.fit_voltage, self.fit_voltage_normalized

#--------------------------------------------------------------------------------------------------------------------------------
    def double_exponential(self, t, A, tau1, tau2, td):
        self.double_exponential = A * (np.exp(-(t - td) / tau1) - np.exp(-(t - td) / tau2)) 

    def fit_double_exponential(self):
        # Valores iniciales para los parámetros [A, tau1, tau2, td]
        initial_guess = [self.peak_value, 70e-6, 0.4e-6, 0]

        # Realizar el ajuste de curva.
        popt, pcov = curve_fit(self.double_exponential, self.fit_time, self.fit_voltage, p0=initial_guess, maxfev=5000)

        # Parámetros ajustados.
        A_fit, tau1_fit, tau2_fit, td_fit = popt

        print(f"Parámetros ajustados: A={A_fit}, tau1={tau1_fit}, tau2={tau2_fit}, td={td_fit}")

        return popt