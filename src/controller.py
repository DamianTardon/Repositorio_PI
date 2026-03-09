import time
from PySide6.QtCore import QObject, QThread, Signal, Slot, QRegularExpression
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QRegularExpressionValidator, QIntValidator

class WaitWaveformThread(QThread):
    # Hilo en segundo plano para esperar el disparo del osciloscopio sin congelar la GUI.
    wave_detected = Signal()
    error_occurred = Signal(str)

    def __init__(self, oscilloscope):
        super().__init__()
        self.oscilloscope = oscilloscope
        self._is_running = True

    def run(self):
        try:
            # Armar el disparo único.
            self.oscilloscope.set_single_trigger()

            # Bucle de espera de disparo.
            while self._is_running:
                state = self.oscilloscope.get_trigger_state()
                if state == 'Disparado':
                    self.wave_detected.emit()
                    break
                time.sleep(0.2)  # Pausa de 200ms.
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False

class AutoAdjustTriggerThread(QThread):
    # Hilo para buscar el umbral de ruido del trigger automáticamente.
    finished_adjust = Signal(float)
    error_occurred = Signal(str)

    def __init__(self, oscilloscope):
        super().__init__()
        self.oscilloscope = oscilloscope

    def run(self):
        try:
            current_level = self.oscilloscope.get_trigger_level()
            slope = self.oscilloscope.get_trigger_slope()

            # Definir el paso de incremento.
            step = 0.05 if slope == 'Positivo' else -0.05

            # Buscar el umbral de ruido del trigger.
            while True:
                self.oscilloscope.set_single_trigger()
                time.sleep(0.1) # Tiempo para que el hardware arme el trigger.

                state = self.oscilloscope.get_trigger_state()
                if state == 'Disparado':
                    current_level += step
                    self.oscilloscope.set_trigger_level(current_level)
                    continue
                else:
                    # Si no disparó, esperar 1 segundo.
                    time.sleep(1.0)
                    state = self.oscilloscope.get_trigger_state()
                    
                    if state == 'Disparado':
                        current_level += step
                        self.oscilloscope.set_trigger_level(current_level)
                        continue
                    else:
                        # Si después de 1 segundo no disparó, encontró el umbral.
                        self.finished_adjust.emit(current_level)
                        break

        except Exception as e:
            self.error_occurred.emit(str(e))

class MainController(QObject):
    def __init__(self, ui, oscilloscope, file_manager, analyzer_class):
        super().__init__()
        self.ui = ui
        self.osc = oscilloscope
        self.fm = file_manager
        self.AnalyzerClass = analyzer_class

        # Variables de estado del ensayo.
        self.ref_analyzer = None
        self.last_acquired_data = None  # Almacena (inBuffer, waveform, dt) temporalmente.
        self.onda_count = 0

        # Hilos.
        self.wait_thread = None
        self.auto_thread = None

        self._setup_ui()
        self._connect_signals()

        # Intentar conexión automática inicial.
        self.osc.connect(None)

    def _setup_ui(self):
        # 1. Variables continuas (Editables). 
        self.ui.ch1_offset.setEditable(True)
        self.ui.ch2_offset.setEditable(True)
        self.ui.delay_valor.setEditable(True)
        self.ui.trigger_nivel_valor.setEditable(True)

        # 2. Definir Validadores.
        # Validador Entero positivo.
        validador_enteros = QIntValidator(0, 9999)

        # Validador Decimal positivo.
        regla_dec_pos = QRegularExpression(r"^[0-9]+(\.[0-9]+)?$")
        validador_dec_pos = QRegularExpressionValidator(regla_dec_pos)

        # Validador Decimal negativo/positivo. ("-?" significa guion opcional)
        regla_dec_signo = QRegularExpression(r"^-?[0-9]+(\.[0-9]+)?$")
        validador_dec_signo = QRegularExpressionValidator(regla_dec_signo)

        # 3. Aplicar a Condiciones Ambientales.
        self.ui.entrada_humedad.setValidator(validador_enteros)
        self.ui.entrada_temperatura.setValidator(validador_dec_pos)
        self.ui.entrada_presion.setValidator(validador_dec_pos)

        # 4. Aplicar a Atenuaciones del Sistema (Siempre positivos).
        self.ui.atenuacion_ch1_divisor_resistivo.setValidator(validador_dec_pos)
        self.ui.atenuacion_ch1_atenuador.setValidator(validador_dec_pos)
        self.ui.atenuacion_ch2_divisor_resistivo.setValidator(validador_dec_pos)
        self.ui.atenuacion_ch2_atenuador.setValidator(validador_dec_pos)

        # 5. Aplicar a los ComboBox Editables (Pueden ser negativos).
        # Ahora esto funciona perfectamente porque ya son editables.
        self.ui.ch1_offset.lineEdit().setValidator(validador_dec_signo)
        self.ui.ch2_offset.lineEdit().setValidator(validador_dec_signo)
        self.ui.delay_valor.lineEdit().setValidator(validador_dec_signo)
        self.ui.trigger_nivel_valor.lineEdit().setValidator(validador_dec_signo)

        # 6. Inicializar las listas desplegables.
        v_divs = ["2", "5", "10", "20", "50", "100", "200", "500"]
        v_units = ["mV", "V"]
        t_divs = ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"]
        t_units = ["ns", "us", "ms", "s"]

        # Escala Vertical.
        for combo in [self.ui.ch1_tension_valor, self.ui.ch2_tension_valor]:
            combo.addItems(v_divs)
        for combo in [self.ui.ch1_tension_unidad, self.ui.ch2_tension_unidad]:
            combo.addItems(v_units)

        # Escala Horizontal.
        self.ui.tiempo_valor.addItems(t_divs)
        self.ui.tiempo_unidad.addItems(t_units)

        # Sugerencias iniciales para variables continuas.
        self.ui.ch1_offset.addItems(["0.0", "1.0", "-1.0"])
        self.ui.trigger_nivel_valor.addItems(["0.0", "0.5", "1.0", "2.0"])

        # 7. Estado inicial de habilitadores.
        self._toggle_atenuaciones()

    def _connect_signals(self):
        # Vincula los botones y eventos de la GUI a sus funciones.

        # Botones principales.
        self.ui.btn_buscar_instrumento.clicked.connect(self.buscar_instrumento_manual)
        self.ui.btn_crear_carpeta.clicked.connect(self.crear_nuevo_proyecto)
        self.ui.btn_esperarOnda.clicked.connect(self.iniciar_espera_onda)
        self.ui.btn_capturarOnda.clicked.connect(self.guardar_onda_capturada)
        self.ui.btn_autoajustar.clicked.connect(self.iniciar_autoajuste)

        # Habilitadores.
        self.ui.habilitador_atenuaciones.stateChanged.connect(self._toggle_atenuaciones)

        # Handlers de Escala Vertical.
        self.ui.ch1_tension_valor.currentTextChanged.connect(lambda v: self._update_v_scale(1, v, self.ui.ch1_tension_unidad.currentText()))
        self.ui.ch1_tension_unidad.currentTextChanged.connect(lambda u: self._update_v_scale(1, self.ui.ch1_tension_valor.currentText(), u))
        self.ui.ch2_tension_valor.currentTextChanged.connect(lambda v: self._update_v_scale(2, v, self.ui.ch2_tension_unidad.currentText()))
        self.ui.ch2_tension_unidad.currentTextChanged.connect(lambda u: self._update_v_scale(2, self.ui.ch2_tension_valor.currentText(), u))

        # Handler de Escala Horizontal.
        self.ui.tiempo_valor.currentTextChanged.connect(self._update_t_scale)
        self.ui.tiempo_unidad.currentTextChanged.connect(self._update_t_scale)

        # Handlers de Variables Continuas.
        self.ui.ch1_offset.lineEdit().editingFinished.connect(lambda: self._update_offset(1, self.ui.ch1_offset.currentText()))
        self.ui.ch2_offset.lineEdit().editingFinished.connect(lambda: self._update_offset(2, self.ui.ch2_offset.currentText()))
        self.ui.delay_valor.lineEdit().editingFinished.connect(lambda: self._update_delay(self.ui.delay_valor.currentText()))
        self.ui.trigger_nivel_valor.lineEdit().editingFinished.connect(lambda: self._update_trigger_level(self.ui.trigger_nivel_valor.currentText()))

        # Flanco de Trigger.
        self.ui.trigger_f_positivo.toggled.connect(lambda checked: self.osc.set_trigger_slope(0) if checked else None)
        self.ui.trigger_f_negativo.toggled.connect(lambda checked: self.osc.set_trigger_slope(1) if checked else None)

    # --- Funciones Lógicas ---

    def crear_nuevo_proyecto(self):
        item_num = self.ui.entrada_item_numero.text()
        item_anio = self.ui.entrada_item_anio.text()
        cliente = self.ui.entrada_cliente.text()
        nombre_carpeta = f"{item_num}-{item_anio} - {cliente}"

        self.fm.__init__(nombre_carpeta)

        # Reiniciar memoria del ensayo.
        self.ref_analyzer = None
        self.onda_count = 0
        self.ui.onda_n_nombre.setText("Proyecto inicializado")
        QMessageBox.information(None, "Éxito", f"Memoria reiniciada.\nCarpetas creadas para:\n{nombre_carpeta}")

    def buscar_instrumento_manual(self):
        # Llamada libre ya que es iniciada por el usuario.
        self.osc.connect(None) 
        if self.osc.dso:
            QMessageBox.information(None, "Conexión", "Instrumento conectado correctamente.")
        else:
            QMessageBox.warning(None, "Error", "No se encontró el instrumento.")

    def iniciar_espera_onda(self):
        if not self.osc.dso:
            QMessageBox.warning(None, "Error", "El osciloscopio no está conectado.")
            return

        self.ui.btn_esperarOnda.setEnabled(False)
        self.ui.btn_esperarOnda.setText("Esperando...")

        self.wait_thread = WaitWaveformThread(self.osc)
        self.wait_thread.wave_detected.connect(self.procesar_onda_detectada)
        self.wait_thread.error_occurred.connect(self._manejar_error_hilo)
        self.wait_thread.start()

    @Slot()
    def procesar_onda_detectada(self):
        self.ui.btn_esperarOnda.setEnabled(True)
        self.ui.btn_esperarOnda.setText("Iniciar")

        # Determinar canal activo principal.
        canal_activo = 1 if self.ui.habilitador_ch1.isChecked() else (2 if self.ui.habilitador_ch2.isChecked() else None)

        if canal_activo is None:
            QMessageBox.warning(None, "Cuidado", "Se detectó disparo, pero no hay canales habilitados para leer.")
            return

        # Descargar bloque de datos.
        inBuffer, waveform, dt = self.osc.get_block_data(canal_activo)
        if waveform is None:
            return

        # Guardar temporalmente hasta que el usuario accione el botón Guardar.
        self.last_acquired_data = (inBuffer, waveform, dt)

        # Invertir atenuaciones del sistema para determinar el valor real de la onda.
        waveform_real = self._aplicar_atenuaciones_hardware(waveform, canal_activo)

        # Instanciar analizador para mostrar valores.
        temp_analyzer = self.AnalyzerClass(waveform_real, dt, sigma_fit=1.0)
        
        try:
            if self.ref_analyzer is None:
                temp_analyzer.ref_lightning_impulse()
            else:
                temp_analyzer.lightning_impulse(self.ref_analyzer)

            # Actualizar GUI con resultados.
            res = temp_analyzer.results
            self.ui.v_valor.setText(f"{res['Ut']/1000:.2f}") # Pasando a kV.
            self.ui.t1_valor.setText(f"{res['T1']*1e6:.2f}") # Pasando a us.
            self.ui.t2_valor.setText(f"{res['T2']*1e6:.2f}") # Pasando a us.
            self.ui.os_valor.setText(f"{res['Beta_prime']:.2f}")

            # TODO: Aquí irá el código de actualización del gráfico (self.ui.grafico_vista)
            print("Onda procesada y lista para ser guardada.")

        except Exception as e:
            QMessageBox.critical(None, "Error de Análisis", str(e))

    def guardar_onda_capturada(self):
        if not self.last_acquired_data:
            QMessageBox.warning(None, "Aviso", "No hay ninguna onda adquirida en memoria para guardar.")
            return

        inBuffer, waveform, dt = self.last_acquired_data
        canal_activo = 1 if self.ui.habilitador_ch1.isChecked() else 2

        self.onda_count += 1
        nombre_base = f"Onda_{self.onda_count:02d}"

        # Guardar Archivos.
        bin_path = self.fm.get_new_name(prefijo=nombre_base, extension=".bin")
        self.fm.create_bin_int16(inBuffer, bin_path)

        # Analizar en profundidad para fijar estado
        waveform_real = self._aplicar_atenuaciones_hardware(waveform, canal_activo)
        analyzer = self.AnalyzerClass(waveform_real, dt, sigma_fit=1.0)

        if self.ref_analyzer is None:
            analyzer.ref_lightning_impulse()
            self.ref_analyzer = analyzer
            tipo_onda = "Referencia"
        else:
            analyzer.lightning_impulse(self.ref_analyzer)
            tipo_onda = "Ensayo"

        # Exportar a HDF5 (Usando el time_axis generado por el analyzer).
        h5_path = self.fm.get_new_name(prefijo=nombre_base, extension=".h5")
        self.fm.create_hdf5(analyzer.time_axis, waveform_real, h5_path)

        # Actualizar Interfaz.
        self.ui.onda_n_nombre.setText(f"{nombre_base} ({tipo_onda})")

        # Limpiar buffer temporal.
        self.last_acquired_data = None
        QMessageBox.information(None, "Guardado", f"{nombre_base} guardada exitosamente.")

    def iniciar_autoajuste(self):
        if not self.osc.dso:
            return

        self.ui.btn_autoajustar.setEnabled(False)
        self.ui.btn_autoajustar.setText("Ajustando...")

        self.auto_thread = AutoAdjustTriggerThread(self.osc)
        self.auto_thread.finished_adjust.connect(self._autoajuste_finalizado)
        self.auto_thread.error_occurred.connect(self._manejar_error_hilo)
        self.auto_thread.start()

    @Slot(float)
    def _autoajuste_finalizado(self, umbral_encontrado):
        self.ui.btn_autoajustar.setEnabled(True)
        self.ui.btn_autoajustar.setText("Autoajustar")

        # Actualizar la lista desplegable con el valor encontrado.
        nuevo_valor_str = f"{umbral_encontrado:.3f}"
        self.ui.trigger_nivel_valor.setCurrentText(nuevo_valor_str)
        QMessageBox.information(None, "Autoajuste", f"Umbral detectado en {nuevo_valor_str} V.")


    # --- Utilidades y Actualizadores de Hardware ---

    def _aplicar_atenuaciones_hardware(self, waveform, canal):
        # Aplica la matemática de los divisores resistivos cargados en la GUI.
        if not self.ui.habilitador_atenuaciones.isChecked():
            return waveform # Si no está habilitado, retorna la onda pura.

        try:
            if canal == 1:
                divisor = float(self.ui.atenuacion_ch1_divisor_resistivo.text() or 1.0)
                atenuador = float(self.ui.atenuacion_ch1_atenuador.text() or 1.0)
            else:
                divisor = float(self.ui.atenuacion_ch2_divisor_resistivo.text() or 1.0)
                atenuador = float(self.ui.atenuacion_ch2_atenuador.text() or 1.0)

            return waveform * divisor * atenuador
        except ValueError:
            return waveform

    def _aplicar_atenuaciones_hardware(self, waveform, canal):
            try:
                if canal == 1:
                    divisor = float(self.ui.atenuacion_ch1_divisor_resistivo.text() or 1.0)
                    atenuador = float(self.ui.atenuacion_ch1_atenuador.text() or 1.0)
                else:
                    divisor = float(self.ui.atenuacion_ch2_divisor_resistivo.text() or 1.0)
                    atenuador = float(self.ui.atenuacion_ch2_atenuador.text() or 1.0)

                return waveform * divisor * atenuador

            except ValueError:
                # Si el usuario ingresa una letra por error, asumimos factor 1.0 temporalmente
                # para no frenar abruptamente la ejecución del hilo.
                return waveform

    def _toggle_atenuaciones(self):
        estado = self.ui.habilitador_atenuaciones.isChecked()
        self.ui.atenuacion_ch1_divisor_resistivo.setEnabled(estado)
        self.ui.atenuacion_ch1_atenuador.setEnabled(estado)
        self.ui.atenuacion_ch2_divisor_resistivo.setEnabled(estado)
        self.ui.atenuacion_ch2_atenuador.setEnabled(estado)

    def _update_v_scale(self, channel, val_str, unit_str):
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_channel_scale(channel, scale)

    def _update_t_scale(self, *args):
        val_str = self.ui.tiempo_valor.currentText()
        unit_str = self.ui.tiempo_unidad.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_timebase_scale(scale)

    def _update_offset(self, channel, val_str):
        try:
            val = float(val_str)
            self.osc.set_channel_offset(channel, val)
        except ValueError:
            pass # Ignorar si el usuario teclea letras.

    def _update_delay(self, val_str):
        try:
            val = float(val_str)
            self.osc.set_timebase_position(val)
        except ValueError:
            pass

    def _update_trigger_level(self, val_str):
        try:
            val = float(val_str)
            self.osc.set_trigger_level(val)
        except ValueError:
            pass

    @Slot(str)
    def _manejar_error_hilo(self, error_msg):
        self.ui.btn_esperarOnda.setEnabled(True)
        self.ui.btn_autoajustar.setEnabled(True)
        self.ui.btn_esperarOnda.setText("Iniciar")
        self.ui.btn_autoajustar.setText("Autoajustar")
        QMessageBox.critical(None, "Error de Comunicación", f"Se produjo un error:\n{error_msg}")