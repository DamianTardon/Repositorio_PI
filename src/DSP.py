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
        self.zeroed_voltage = None
        self.offset_value = 0.0
        self.peak_value = 0.0
        self.polarity = None
        self.idx_peak = None
        self.norm_voltage = None
        self.factor = 1.0
        self.start_slice = None
        self.end_slice = None
        self.fit_voltage = None
        self.fit_time = None
        self.base_curve = None
        self.Ub = 0.0
        self.residual_curve = None
        self.filter_coeffs = None
        self.filtered_residual = None
        self.test_voltage_curve = None
        self.Ut = 0.0
        

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
        # c) Encontrar el valor extremo, Ue, de la curva registrada compensada en offset, U0(t).
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
        
        # 4. Invertir polaridad si es negativa.
        self.zeroed_voltage = self.zeroed_voltage * self.factor
        self.peak_value = original_peak * self.factor

        # 5. Normalizar la señal.
        self.norm_voltage = self.zeroed_voltage / self.peak_value
        
        return self.peak_value, self.polarity
    
    def cutting_signal(self):
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
        
        print(f"Pico = {self.peak_value/1000:.2f} kV")
        print(f"umbral 20% = {threshold_20/1000:.2f} kV, ID = {self.start_slice}, V = {self.zeroed_voltage[self.start_slice]/1000:.2f} kV")
        print(f"umbral 40% = {threshold_40/1000:.2f} kV, ID = {self.end_slice}, V = {self.zeroed_voltage[self.end_slice]/1000:.2f} kV")

        return self.fit_time, self.fit_voltage, self.fit_voltage_normalized

#--------------------------------------------------------------------------------------------------------------------------------
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
        # Insertar los valores calculados
        result[mask] = val
        
        return result
    
    def fit_base_curve(self):
        # g) Ajustar la función de doble exponencial a los datos recortados.
        if self.fit_voltage is None or self.fit_time is None:
            raise ValueError("Falta segmentar los datos para el ajuste.")
        
        # 1. Estimación de parámetros iniciales.
        p0_U = self.peak_value 
        p0_tau1 = 70e-6
        p0_tau2 = 0.4e-6
        p0_td = self.fit_time[0]
        initial_guess = [p0_U, p0_tau1, p0_tau2, p0_td]

        # 2. Ejecutar el ajuste de curva (Levenberg-Marquardt).
        try:
            # Bounds: Ayuda a que no converja a valores físicos imposibles (ej. tau negativo)
            # U > 0, tau > 0, td puede ser cualquiera (dentro del rango de tiempo)
            # A veces no poner bounds ayuda a LM, pero ponerlos fuerza a usar TRF (Trust Region Reflective)
            # Probaremos primero sin bounds estrictos o solo positividad simple si falla.
            
            popt, pcov = curve_fit(
                self._double_exponential_func, 
                self.fit_time, 
                self.fit_voltage, 
                p0 = initial_guess,
                maxfev = 10000
            )

            self.fitted_params = {
                'U': popt[0],
                'tau1': popt[1],
                'tau2': popt[2],
                'td': popt[3]
            }
            self.popt = popt

            print("Ajuste completado con exito.")
            print(f"A = {self.fitted_params['U']/1e3:.2f} kV, tau1 = {self.fitted_params['tau1']*1e6:.2f} µs, tau2 = {self.fitted_params['tau2']*1e6:.2f} µs, td = {self.fitted_params['td']*1e6:.2f} µs")

        except RuntimeError as e:
            raise RuntimeError(f"Falló el ajuste de curva : {e}")

        # 3. Generar la función ajustada con los parámetros encontrados.
        self.fitted_curve = self._double_exponential_func(self.fit_time, 
                                                          self.fitted_params['U'], 
                                                          self.fitted_params['tau1'], 
                                                          self.fitted_params['tau2'], 
                                                          self.fitted_params['td'])
        return
    
    def construct_base_curve(self):
        # h) Construir la curva base Um(t).
        if not hasattr(self, 'popt') or self.popt is None:
            raise ValueError("Falta ejecutar fit_base_curve.")

        self.base_curve = self._double_exponential_func(self.time_axis, *self.popt)

        # n) Determinar el máximo de la curva base (Ub)
        self.Ub = np.max(self.base_curve)
        
        return self.base_curve, self.Ub
    
    def calculate_residual_curve(self):
        # i) Obtener la curva residual. R(t) = U0(t) - Um(t).
        if self.zeroed_voltage is None:
            raise ValueError("Falta la señal U0(t). Ejecutar primero remove_offset.")
        if self.base_curve is None:
            raise ValueError("Falta la curva base Um(t). Ejecutar primero construct_base_curve.")

        self.residual_curve = self.zeroed_voltage - self.base_curve

        return self.residual_curve
    
    def create_digital_filter(self):
        # j) Crear el filtro digital.
        d = 2.2e-12 

        # Cálculo de la constante intermedia c.
        c = np.tan((np.pi * self.sample_rate) / np.sqrt(d))
        
        # Cálculo de coeficientes del filtro.
        b0 = c / (1 + c)
        b1 = b0
        a1 = (1 - c) / (1 + c)
        
        # La norma escribe la ecuación recursiva como:
        # y(i) = b0*x(i) + b1*x(i-1) + a1*y(i-1)
        #
        # Scipy 'filtfilt' usa la convención estándar de procesamiento de señales:
        # a0*y[n] + a1*y[n-1] = b0*x[n] + b1*x[n-1]
        
        b = np.array([b0, b1])   # Constantes de X
        a = np.array([1.0, -a1]) # Constantes de Y
        
        self.filter_coeffs = (b, a)
        return b, a

    def filter_to_residual(self):
        # k) Aplicar el filtro digital a la curva residual R(t).
        if self.residual_curve is None:
            raise ValueError("Falta la curva residual. Ejecuta primero calculate_residual_curve.")
            
        # 1. Calcular los coeficientes del filtro.
        b, a = self.create_digital_filter()
        
        # 2. Aplicar el filtro de fase cero, para obtener la curva residual filtrada Rf(t).
        self.filtered_residual = signal.filtfilt(b, a, self.residual_curve)
        
        return self.filtered_residual
    
    def construct_test_voltage_curve(self):
        # l) Obtener la curva de tensión de ensayo Ut(t) = Um(t) + Rf(t).

        # Validaciones de estado
        if self.base_curve is None:
            raise ValueError("Falta la curva base Um(t). Ejecutar primero construct_base_curve.")
        if self.filtered_residual is None:
            raise ValueError("Falta el residual filtrado Rf(t). Ejecutar primero filter_to_residual.")

        self.test_voltage_curve = self.base_curve + self.filtered_residual

        # m (Parcial): Calcular el valor de la tensión de ensayo Ut
        self.Ut = np.max(self.test_voltage_curve)

        return self.test_voltage_curve
    
    def calculate_parameters(self):
        if self.test_voltage_curve is None:
            raise ValueError("Falta la curva de tensión de prueba Ut(t). Ejecuta construct_test_voltage_curve.")

        # m) Calcular el valor de la tensión de ensayo, Ut, y los parámetros de tiempo.
        Ut = np.max(self.test_voltage_curve)
        idx_peak_Ut = np.argmax(self.test_voltage_curve)
        
        # Separamos frente y cola de la curva de prueba para las búsquedas
        t_axis = self.time_axis
        Ut_curve = self.test_voltage_curve
        
        front_v = Ut_curve[:idx_peak_Ut]
        front_t = t_axis[:idx_peak_Ut]
        
        tail_v = Ut_curve[idx_peak_Ut:]
        tail_t = t_axis[idx_peak_Ut:]

        # --- Función auxiliar para interpolar tiempo dado un voltaje ---
        def _get_time_at_voltage(voltage_array, time_array, target_voltage, slope="rising"):
            # Buscamos el índice donde se cruza el umbral
            if slope == "rising":
                # Para el frente (subida), buscamos el último punto menor al target
                # Usamos la lógica de 'searchsorted' que es muy eficiente en arrays ordenados
                idx = np.searchsorted(voltage_array, target_voltage)
            else:
                # Para la cola (bajada), el array va de mayor a menor. 
                # Invertimos para usar searchsorted o usamos lógica manual
                # Lógica manual robusta: buscar primer punto menor al target
                idx = np.argmax(voltage_array < target_voltage)
            
            # Interpolación Lineal: t = t1 + (V_target - V1) * (dt/dV)
            if idx == 0 or idx >= len(voltage_array):
                return time_array[idx] if idx < len(voltage_array) else time_array[-1]
            
            v1 = voltage_array[idx-1]
            v2 = voltage_array[idx]
            t1 = time_array[idx-1]
            t2 = time_array[idx]
            
            if v2 == v1: return t1
            
            return t1 + (target_voltage - v1) * ((t2 - t1) / (v2 - v1))

        # Calcular Tiempo de Frente (T1).
        # Umbrales: 30% y 90% de Ut.
        v30 = 0.3 * Ut
        v90 = 0.9 * Ut
        
        t30 = _get_time_at_voltage(front_v, front_t, v30, slope="rising")
        t90 = _get_time_at_voltage(front_v, front_t, v90, slope="rising")
        
        Tab = t90 - t30
        T1 = Tab / 0.6
        
        # Calcular Origen Virtual (O1).
        O1 = t30 - 0.3 * T1
        O2 = t30 - 0.5 * Tab

        # Calcular Tiempo hasta el semivalor (T2).
        # Umbral: 50% de Ut en la cola.
        v50 = 0.5 * Ut
        t50 = _get_time_at_voltage(tail_v, tail_t, v50, slope="falling")
        
        # T2 es el intervalo entre el origen virtual y el punto de 50%.
        T2 = t50 - O1
        T3 = t50 - O2

        # o) Calcular la sobreelevación relativa (Beta').
        Ue = self.peak_value
        Ub = self.Ub
        
        beta_prime = 100 * (Ue - Ub) / Ue

        # Empaquetar resultados:
        self.results = {
            "Ut": Ut,                   # Voltaje pico de ensayo (kV)
            "T1": T1,                   # Tiempo de frente (s)
            "T2": T2,                   # Tiempo de cola (s)
            "O1": O1,                   # Origen virtual (s)
            "Beta_prime": beta_prime,   # Sobreelevación relativa (%)
            "Ue": Ue,                   # Pico original
            "Ub": Ub                    # Pico base
        }
        
        return self.results