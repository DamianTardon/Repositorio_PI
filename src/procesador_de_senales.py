import numpy as np
from scipy.optimize import curve_fit
from scipy import signal

class LightningImpulseAnalyzer:
    def __init__(self, voltage_data, sample_rate):
        # Datos de entrada:
        self.raw_voltage = np.array(voltage_data)
        self.sample_rate = sample_rate

        # Generar array de tiempo automáticamente: t = index * intervalo
        self.time_axis = np.arange(len(self.raw_voltage)) * self.sample_rate

        # Parámetros calculados:
        self.pre_trigger_percent = 0.03
        self.offset_value = 0.0
        self.zeroed_curve = None
        self.zeroed_curve_abs = None
        self.idx_peak = None
        self.peak_value = 0.0
        self.Ue = 0.0
        self.polarity = None
        self.factor = 1.0
        self.norm_voltage = None
        self.start_slice = None
        self.end_slice = None
        self.fit_voltage = None
        self.fit_voltage_normalized = None
        self.fit_time = None
        self.fitted_params = None
        self.popt = None
        self.fitted_curve = None
        self.base_curve = None
        self.Ub = 0.0
        self.residual_curve = None
        self.filter_coeffs = None
        self.filtered_residual = None
        self.test_voltage_curve_abs = None
        self.test_voltage_curve = None
        self.Ut = 0.0
        self.idx_peak_Ut = None
        self.results = None

    def _remove_offset(self):
        # a) Encontrar el nivel de base de la curva registrada.
        # 1. Calcular cantidad de muestras de ruido de fondo.
        total_samples = len(self.raw_voltage)
        n_samples_background = int(total_samples * self.pre_trigger_percent)

        if n_samples_background < 1:
            raise ValueError("Error: No hay suficientes muestras de pre-trigger para calcular el offset.")

        # 2. Calcular el promedio del ruido (Offset).
        background_noise = self.raw_voltage[:n_samples_background]
        self.offset_value = np.mean(background_noise)

        # b) Eliminar el offset de la curva registrada.
        # 1. Restar el offset a toda la señal.
        self.zeroed_curve = self.raw_voltage - self.offset_value

        return

    def _polarity_normalization(self):
        if self.zeroed_curve is None:
            raise ValueError("Error: Falta quitar el offset de la onda.")

        # c) Encontrar el valor extremo, Ue, de la curva registrada compensada en offset, U0(t).
        # 1. Encontrar el índice del máximo valor absoluto.
        self.idx_peak = np.argmax(np.abs(self.zeroed_curve))
        self.Ue = self.zeroed_curve[self.idx_peak]

        # 2. Determinar la polaridad de la señal.
        if self.Ue >= 0:
            self.polarity = "Positiva"
            self.factor = 1.0
        else:
            self.polarity = "Negativa"
            self.factor = -1.0

        self.zeroed_curve_abs = self.zeroed_curve * self.factor
        self.peak_value = self.zeroed_curve_abs[self.idx_peak]

        return
    
    def _normalize_waveform(self):
        if self.zeroed_curve_abs is None:
            raise ValueError("Error: Falta calcular el offset de la onda.")

        self.norm_voltage = self.zeroed_curve_abs / self.peak_value
        """
        # ---------------------------------------------------------------------------------------------
        front_data = self.zeroed_curve[:self.idx_peak]
        idx = self._find_limit_index(front_data, 0, mode="front")
        self.zeroed_curve[:idx+1] = 0
        # ---------------------------------------------------------------------------------------------
        """
        return
    
    @staticmethod
    def _find_limit_index(v_array, threshold, mode="front"):
        if mode == "front":
            # Invierte el array para que vaya en sentido decreciente.
            front_reversed = v_array[::-1]

            # Buscar el primer valor que sea menor que el umbral.
            idx_reversed = np.argmax(front_reversed < threshold)

            if idx_reversed == 0 and front_reversed[0] >= threshold:
                 raise ValueError("Error: No se encontraron datos bajo el umbral en el frente.")

            # Convertir el índice invertido al índice original del segmento.
            idx = (len(v_array) - 1) - idx_reversed
        elif mode == "tail":
            idx = np.argmax(v_array < threshold)

            # Validación:
            if idx == 0 and v_array[0] < threshold:
                 raise ValueError("Error: El máximo del segmento de datos es menor que el umbral.") # Analizar eliminar linea de codigo.
            elif idx == 0:
                 raise ValueError("Error: La señal no cae por debajo del umbral en la cola. La onda se cortó antes o tiene un tiempo de cola muy largo")
        else:
            raise ValueError("Modo desconocido. Use 'front' o 'tail'.")

        return idx

    def _cutting_signal(self):
        if self.peak_value is None or self.norm_voltage is None:
            raise ValueError("Error: Falta normalizar la onda.")

        front_data = self.zeroed_curve_abs[:self.idx_peak]
        tail_data = self.zeroed_curve_abs[self.idx_peak:]

        threshold_20 = 0.2 * self.peak_value
        threshold_40 = 0.4 * self.peak_value

        # d) Encontrar la última muestra en el frente inferior a 0,2 * Ue.
        # 1. Buscar índice del 20% en el frente.
        idx_20 = self._find_limit_index(front_data, threshold_20, mode="front")

        # 2. Buscar índice del 40% en la cola (retorna índice relativo a tail_data)
        idx_40_local = self._find_limit_index(tail_data, threshold_40, mode="tail")
        idx_40 = self.idx_peak + idx_40_local

        # Limites inferior y superior:
        self.start_slice = idx_20 + 1
        self.end_slice = idx_40 + 1

        self.fit_voltage = self.zeroed_curve_abs[self.start_slice:self.end_slice]
        self.fit_voltage_normalized = self.norm_voltage[self.start_slice:self.end_slice]
        self.fit_time = self.time_axis[self.start_slice:self.end_slice]

        return

    @staticmethod
    def _double_exponential_func(t, U, tau1, tau2, td):
        dt = t - td
        # Máscara de seguridad. Para evitar que diverja el ajuste de curva.
        mask = dt >= 0
        # Crear el contenedor de resultados.
        result = np.zeros_like(dt, dtype=np.float64)
        # Calcular solo sobre los tiempos válidos (positivos).
        valid_dt = dt[mask]
        val = U * (np.exp(-valid_dt / tau1) - np.exp(-valid_dt / tau2))
        # Insertar los valores calculados.
        result[mask] = val

        return result

    def _fit_base_curve(self):
        # g) Ajustar la función de doble exponencial a los datos recortados.
        if self.fit_voltage is None or self.fit_time is None:
            raise ValueError("Error: Falta segmentar los datos de la onda para el ajuste.")

        # 1. Estimación de parámetros iniciales.
        p0_U = self.peak_value 
        p0_tau1 = 70e-6
        p0_tau2 = 0.4e-6
        p0_td = self.fit_time[0]
        initial_guess = [p0_U, p0_tau1, p0_tau2, p0_td]

        #idx_peak_in_slice = np.argmax(np.abs(self.fit_voltage))
        #sigma = np.ones_like(self.fit_voltage)
        #sigma[:idx_peak_in_slice + 5] = 0.5

        # 2. Ejecutar el ajuste de curva (Levenberg-Marquardt).
        try:
            popt, pcov = curve_fit(
                self._double_exponential_func, 
                self.fit_time, 
                self.fit_voltage, 
                p0 = initial_guess,
                #sigma = sigma,
                #absolute_sigma = False,
                maxfev = 10000
            )

            self.fitted_params = {
                'U': popt[0],
                'tau1': popt[1],
                'tau2': popt[2],
                'td': popt[3]
            }
            self.popt = popt

        except RuntimeError as e:
            raise RuntimeError(f"Falló el ajuste de curva : {e}")
 
        # 3. Generar la función ajustada con los parámetros encontrados.
        self.fitted_curve = self._double_exponential_func(self.fit_time, 
                                                          self.fitted_params['U'], 
                                                          self.fitted_params['tau1'], 
                                                          self.fitted_params['tau2'], 
                                                          self.fitted_params['td'])

        return

    def _construct_base_curve(self):
        # h) Construir la curva base Um(t).
        if self.popt is None:
            raise ValueError("Error: Falta ejecutar fit_base_curve.")

        self.base_curve = self._double_exponential_func(self.time_axis, *self.popt)

        # n) Determinar el máximo de la curva base (Ub).
        self.Ub = np.max(self.base_curve)

        return

    def _calculate_residual_curve(self):
        # i) Obtener la curva residual: R(t) = U0(t) - Um(t).
        if self.zeroed_curve_abs is None:
            raise ValueError("Error: Falta quitar el offset de la onda.")
        if self.base_curve is None:
            raise ValueError("Error: Falta encontrar la curva base.")

        self.residual_curve = self.zeroed_curve_abs - self.base_curve

        return

    def _create_digital_filter(self):
        # j) Crear el filtro digital.
        # Constante dada por la norma IEC 60060-1 para el diseño del filtro.
        d = 2.2e-12 

        # Cálculo de la constante intermedia c.
        c = np.tan((np.pi * self.sample_rate) / np.sqrt(d))

        # Cálculo de coeficientes del filtro.
        b0 = c / (1 + c)
        b1 = b0
        a1 = (1 - c) / (1 + c)

        # La norma plantea la ecuación recursiva:
        # y(i) = b0*x(i) + b1*x(i-1) + a1*y(i-1)
        #
        # Scipy 'filtfilt' usa la forma:
        # a0*y[n] + a1*y[n-1] = b0*x[n] + b1*x[n-1]

        b = np.array([b0, b1])
        a = np.array([1.0, -a1])

        self.filter_coeffs = (b, a)
        return b, a

    def _filter_to_residual(self):
        # k) Aplicar el filtro digital a la curva residual R(t).
        if self.residual_curve is None:
            raise ValueError("Error: Falta calcular la curva residual.")

        # 1. Calcular los coeficientes del filtro.
        b, a = self._create_digital_filter()

        # 2. Aplicar el filtro de fase cero, para obtener la curva residual filtrada Rf(t).
        self.filtered_residual = signal.filtfilt(b, a, self.residual_curve)

        return

    def _construct_test_voltage_curve(self):
        # l) Obtener la curva de tensión de ensayo Ut(t) = Um(t) + Rf(t).

        # Validaciones de estado
        if self.base_curve is None:
            raise ValueError("Error: Falta calcular la curva base Um(t).")
        if self.filtered_residual is None:
            raise ValueError("Error: Falta calcular la curva residual filtrada Rf(t).")

        self.test_voltage_curve_abs = self.base_curve + self.filtered_residual
        """
        # ---------------------------------------------------------------------------------------------
        idx = self._find_limit_index(self.test_voltage_curve_abs, 0, mode="front")
        self.test_voltage_curve_abs[:idx+1] = 0
        # ---------------------------------------------------------------------------------------------
        """
        # Devolver signo a la curva:
        self.Ut = np.max(self.test_voltage_curve_abs) * self.factor
        self.test_voltage_curve = self.test_voltage_curve_abs * self.factor

        return

    @staticmethod
    def _linear_interpolation(t_array, v_array, idx_low, target_voltage):
        v1 = v_array[idx_low]
        t1 = t_array[idx_low]

        if idx_low + 1 < len(v_array) and v_array[idx_low + 1] > v1:
            # Indice siguiente.
            idx_high = idx_low + 1
        elif idx_low - 1 >= 0 and v_array[idx_low - 1] > v1:
            # Indice anterior.
            idx_high = idx_low - 1
        else:
            # Caso borde o valor exacto.
            return t1

        v2 = v_array[idx_high]
        t2 = t_array[idx_high]

        # Fórmula: t = t1 + (V_target - V1) * (dt / dV)
        return t1 + (target_voltage - v1) * ((t2 - t1) / (v2 - v1))

    def _calculate_parameters(self):
        if self.test_voltage_curve_abs is None:
            raise ValueError("Error: Falta calcular la curva de tensión de prueba.")

        # m) Calcular el valor de la tensión de ensayo, Ut, y los parámetros de tiempo.
        Ut = np.max(self.test_voltage_curve_abs)
        self.idx_peak_Ut = np.argmax(self.test_voltage_curve_abs)

        # Separa frente y cola de la curva de prueba.
        front_v = self.test_voltage_curve_abs[:self.idx_peak_Ut]
        front_t = self.time_axis[:self.idx_peak_Ut]
        tail_v = self.test_voltage_curve_abs[self.idx_peak_Ut:]
        tail_t = self.time_axis[self.idx_peak_Ut:]

        # Calcular Tiempo de Frente (T1).
        v30 = 0.3 * Ut
        v90 = 0.9 * Ut

        idx_30 = self._find_limit_index(front_v, v30, mode="front")
        idx_90 = self._find_limit_index(front_v, v90, mode="front")

        t30 = self._linear_interpolation(front_t, front_v, idx_30, v30)
        t90 = self._linear_interpolation(front_t, front_v, idx_90, v90)

        Tab = t90 - t30
        T1 = Tab / 0.6

        # Calcular Origen Virtual (O1).
        O1 = t30 - 0.5 * Tab

        # Calcular Tiempo cola (T2).
        v50 = 0.5 * Ut

        idx_50 = self._find_limit_index(tail_v, v50, mode="tail")

        t50 = self._linear_interpolation(tail_t, tail_v, idx_50, v50)

        T2 = t50 - O1

        # o) Calcular la sobreelevación relativa (Beta').
        beta_prime = 100 * (self.peak_value - self.Ub) / self.peak_value

        # Empaquetar resultados:
        self.results = {
            "Ut": self.Ut,              # Voltaje pico de ensayo (kV)
            "T1": T1,                   # Tiempo de frente (s)
            "T2": T2,                   # Tiempo de cola (s)
            "O1": O1,                   # Origen virtual (s)
            "Beta_prime": beta_prime,   # Sobreelevación relativa (%)
            "Ue": self.Ue,              # Pico original
            "Ub": self.Ub               # Pico base
        }
        
        return

    def signal_processing(self):
        # Ejecutar pipeline completo
        self._remove_offset()
        self._polarity_normalization()
        self._normalize_waveform()
        self._cutting_signal()
        self._fit_base_curve()
        self._construct_base_curve()
        self._calculate_residual_curve()
        self._filter_to_residual()
        self._construct_test_voltage_curve()
        self._calculate_parameters()
        return