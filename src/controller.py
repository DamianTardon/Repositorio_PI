import time
from PySide6.QtCore import QObject, QThread, Signal, Slot, QRegularExpression, QTimer
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

        self._setup_ui()
        self._connect_signals()
        if self.osc.dso is not None:
            # Si el instrumento se conectó con éxito en main.py,
            # espera que la GUI esté visible.
            # 100 milisegundos después sincroniza el instrumento con los valores de la GUI.
            QTimer.singleShot(100, self.synchronize_instrument)

    def _setup_ui(self):
        # Validadores.
        # Entero positivo.
        validador_enteros = QIntValidator(0, 9999)
        # Decimal positivo.
        regla_dec_pos = QRegularExpression(r"^[0-9]+(\.[0-9]+)?$")
        validador_dec_pos = QRegularExpressionValidator(regla_dec_pos)
        # Decimal negativo/positivo. ("-?" significa guion opcional)
        regla_dec_signo = QRegularExpression(r"^-?[0-9]+(\.[0-9]+)?$")
        validador_dec_signo = QRegularExpressionValidator(regla_dec_signo)

        # Aplicar a Condiciones Ambientales.
        self.ui.temperatura_bs_valor.setValidator(validador_dec_pos)
        self.ui.temperatura_bh_valor.setValidator(validador_dec_pos)
        self.ui.humedad_relativa_valor.setValidator(validador_dec_pos)
        self.ui.humedad_absoluta_valor.setValidator(validador_dec_pos)
        self.ui.presion_valor.setValidator(validador_dec_pos)

        # Aplicar a Atenuaciones del Sistema (Siempre positivos).
        self.ui.ch1_divisor_resistivo_valor.setValidator(validador_dec_pos)
        self.ui.ch1_atenuador_valor.setValidator(validador_dec_pos)
        self.ui.ch2_divisor_resistivo_valor.setValidator(validador_dec_pos)
        self.ui.ch2_atenuador_valor.setValidator(validador_dec_pos)

        # Aplicar a Offset, delay y nivel de trigger (Pueden ser negativos).
        self.ui.ch1_offset_valor.setValidator(validador_dec_signo)
        self.ui.ch2_offset_valor.setValidator(validador_dec_signo)
        self.ui.delay_valor.setValidator(validador_dec_signo)
        self.ui.trigger_nivel_valor.setValidator(validador_dec_signo)

        # Inicializar las listas desplegables.
        self.valores_tension = {
            "mV": ["2", "5", "10", "20", "50", "100", "200", "500"],
            "V": ["1", "2", "5", "10"]
        }
        self.valores_tiempo = {
            "ns": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
            "us": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
            "ms": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
            "s": ["1", "2.5", "5", "10", "25", "50"]
        }

        # Cargar unidades en las listas desplegables.
        unidades_tension = ["mV", "V"]
        self.ui.ch1_tension_unidad.addItems(unidades_tension)
        self.ui.ch2_tension_unidad.addItems(unidades_tension)
        self.ui.ch1_offset_unidad.addItems(unidades_tension)
        self.ui.ch2_offset_unidad.addItems(unidades_tension)
        self.ui.trigger_nivel_unidad.addItems(unidades_tension)

        unidades_tiempo = ["ns", "us", "ms", "s"]
        self.ui.tiempo_unidad.addItems(unidades_tiempo)
        self.ui.delay_unidad.addItems(unidades_tiempo)

        # Cargar los valores por defecto.
        self.ui.ch1_tension_valor.addItems(self.valores_tension["mV"])
        self.ui.ch2_tension_valor.addItems(self.valores_tension["mV"])
        self.ui.tiempo_valor.addItems(self.valores_tiempo["us"])

        # Cargar los textos por defecto.
        self.ui.ch1_offset_valor.setText("0.0")
        self.ui.ch2_offset_valor.setText("0.0")
        self.ui.delay_valor.setText("0.0")
        self.ui.trigger_nivel_valor.setText("0.0")

        # Estado inicial de habilitadores.
        self.ui.ch1_habilitador.setChecked(True)
        self.ui.ch2_habilitador.setChecked(True)
        self._toggle_attenuations()

    def _connect_signals(self):
        # Botones principales.
        self.ui.btn_buscar_instrumento.clicked.connect(self.search_manual_instrument)
        self.ui.btn_crear_carpeta.clicked.connect(self.create_new_project)
        self.ui.btn_esperar_onda.clicked.connect(self.receive_waveform)
        self.ui.btn_guardar_onda.clicked.connect(self.save_waveform)

        # Habilitadores.
        self.ui.habilitador_atenuaciones.stateChanged.connect(self._toggle_attenuations)

        # Handlers de Escala Vertical.
        self.ui.ch1_tension_valor.currentTextChanged.connect(lambda v: self._update_v_scale(1, v, self.ui.ch1_tension_unidad.currentText()))
        self.ui.ch1_tension_unidad.currentTextChanged.connect(lambda u: self._change_voltage_unit(1, u))

        self.ui.ch2_tension_valor.currentTextChanged.connect(lambda v: self._update_v_scale(2, v, self.ui.ch2_tension_unidad.currentText()))
        self.ui.ch2_tension_unidad.currentTextChanged.connect(lambda u: self._change_voltage_unit(2, u))

        # Handler de Escala Horizontal.
        self.ui.tiempo_valor.currentTextChanged.connect(self._update_t_scale)
        self.ui.tiempo_unidad.currentTextChanged.connect(self._change_time_unit)

        # Handlers de Variables Continuas (Sensibles a valor y unidad).
        self.ui.ch1_offset_valor.editingFinished.connect(lambda: self._update_offset(1))
        self.ui.ch1_offset_unidad.currentTextChanged.connect(lambda: self._update_offset(1))

        self.ui.ch2_offset_valor.editingFinished.connect(lambda: self._update_offset(2))
        self.ui.ch2_offset_unidad.currentTextChanged.connect(lambda: self._update_offset(2))

        self.ui.delay_valor.editingFinished.connect(self._update_delay)
        self.ui.delay_unidad.currentTextChanged.connect(self._update_delay)

        self.ui.trigger_nivel_valor.editingFinished.connect(self._update_trigger_level)
        self.ui.trigger_nivel_unidad.currentTextChanged.connect(self._update_trigger_level)

        # Flanco de Trigger.
        self.ui.trigger_f_positivo.toggled.connect(lambda checked: self.osc.set_trigger_slope(0) if checked else None)
        self.ui.trigger_f_negativo.toggled.connect(lambda checked: self.osc.set_trigger_slope(1) if checked else None)

    # --- Funciones Lógicas ---

    def search_manual_instrument(self):
        import pyvisa

        # Comprobar si el objeto existe y está activo.
        if self.osc.dso is not None:
            try:
                self.osc.dso.query('*IDN?')
                QMessageBox.information(None, "Aviso", "El instrumento ya se encuentra conectado y funcionando correctamente.")
                return
            except Exception:
                # Si falla, limpia la sesión anterior para reconectar.
                self.osc.close()
                self.osc.dso = None

        # Reabrir el gestor de recursos si fue cerrado previamente.
        try:
            self.osc.rm.list_resources()
        except Exception:
            self.osc.rm = pyvisa.ResourceManager('@py')

        # Escanear los puertos de la PC.
        try:
            instrumentos_encontrados = self.osc.rm.list_resources()
        except Exception as e:
            QMessageBox.critical(None, "Error del Sistema", f"No se pudieron escanear los puertos:\n{e}")
            return

        # Conectar al primer equipo que encuentre.
        if instrumentos_encontrados:
            puerto = instrumentos_encontrados[0]
            self.osc.connect(puerto)

            # Verificar el estado de la conexión.
            if self.osc.dso is not None:
                self.synchronize_instrument()
                QMessageBox.information(None, "Conexión Exitosa", f"Instrumento enlazado correctamente en el puerto:\n{puerto}")
            else:
                QMessageBox.warning(None, "Error de Comunicación", f"Se detectó un dispositivo en {puerto}, pero rechazó la conexión.")
        else:
            QMessageBox.warning(None, "Instrumento no encontrado", "No se detectó hardware conectado a la PC.\nRevise el cable USB y asegúrese de que el osciloscopio esté encendido.")

    def create_new_project(self):
        item_num = self.ui.item_numero_valor.text()
        item_anio = self.ui.item_anio_valor.text()
        cliente = self.ui.cliente_valor.text()
        nombre_carpeta = f"{item_num}-{item_anio} - {cliente}"

        self.fm.create_new_structure(nombre_carpeta)

        # Reiniciar memoria del ensayo.
        self.ref_analyzer = None
        self.onda_count = 0
        self.ui.grafico_nombre.setText("Proyecto inicializado")
        QMessageBox.information(None, "Éxito", f"Carpeta creada:\n{nombre_carpeta}")

    def receive_waveform(self):
        if not self.osc.dso:
            QMessageBox.warning(None, "Error", "El osciloscopio no está conectado.")
            return

        self.ui.btn_esperar_onda.setEnabled(False)
        self.ui.btn_esperar_onda.setText("Esperando...")

        self.wait_thread = WaitWaveformThread(self.osc)
        self.wait_thread.wave_detected.connect(self.process_waveform)
        self.wait_thread.error_occurred.connect(self._handle_thread_error)
        self.wait_thread.start()

    @Slot()
    def process_waveform(self):
        self.ui.btn_esperar_onda.setEnabled(True)
        self.ui.btn_esperar_onda.setText("Iniciar")

        # Determinar canal activo principal.
        canal_activo = 1 if self.ui.ch1_habilitador.isChecked() else (2 if self.ui.ch2_habilitador.isChecked() else None)

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
        waveform_real = self._apply_hardware_attenuations(waveform, canal_activo)

        # Instanciar analizador para mostrar valores.
        temp_analyzer = self.AnalyzerClass(waveform_real, dt, sigma_fit=1.0)
        
        try:
            if self.ref_analyzer is None:
                temp_analyzer.ref_lightning_impulse()
            else:
                temp_analyzer.lightning_impulse(self.ref_analyzer)

            # Actualizar GUI con resultados.
            res = temp_analyzer.results
            self.ui.v_valor.setText(f"{res['Ut']/1000:.2f}") # kV.
            self.ui.t1_valor.setText(f"{res['T1']*1e6:.2f}") # us.
            self.ui.t2_valor.setText(f"{res['T2']*1e6:.2f}") # us.
            self.ui.os_valor.setText(f"{res['Beta_prime']:.2f}") # %

            # TODO: Aquí irá el código de actualización del gráfico (self.ui.grafico_vista)
            print("Onda procesada y lista para ser guardada.")

        except Exception as e:
            QMessageBox.critical(None, "Error de Análisis", str(e))

    def save_waveform(self):
        if not self.last_acquired_data:
            QMessageBox.warning(None, "Aviso", "No hay ninguna onda adquirida en memoria para guardar.")
            return

        inBuffer, waveform, dt = self.last_acquired_data
        canal_activo = 1 if self.ui.ch1_habilitador.isChecked() else 2

        self.onda_count += 1
        nombre_base = f"Onda_{self.onda_count:02d}"

        # Guardar Archivos.
        bin_path = self.fm.get_new_name(prefijo=nombre_base, extension=".bin")
        self.fm.create_bin_int16(inBuffer, bin_path)

        # Analizar en profundidad para fijar estado
        waveform_real = self._apply_hardware_attenuations(waveform, canal_activo)
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
        self.ui.grafico_nombre.setText(f"{nombre_base} ({tipo_onda})")

        # Limpiar buffer temporal.
        self.last_acquired_data = None
        QMessageBox.information(None, "Guardado", f"{nombre_base} guardada exitosamente.")

    # --- Utilidades y Actualizadores de Hardware ---

    def _apply_hardware_attenuations(self, waveform, canal):
        try:
            if canal == 1:
                divisor = float(self.ui.ch1_divisor_resistivo_valor.text() or 1.0)
                atenuador = float(self.ui.ch1_atenuador_valor.text() or 1.0)
            else:
                divisor = float(self.ui.ch2_divisor_resistivo_valor.text() or 1.0)
                atenuador = float(self.ui.ch2_atenuador_valor.text() or 1.0)

            return waveform * divisor * atenuador

        except ValueError:
            return waveform

    def _toggle_attenuations(self):
        estado = self.ui.habilitador_atenuaciones.isChecked()
        self.ui.ch1_divisor_resistivo_valor.setEnabled(estado)
        self.ui.ch1_atenuador_valor.setEnabled(estado)
        self.ui.ch2_divisor_resistivo_valor.setEnabled(estado)
        self.ui.ch2_atenuador_valor.setEnabled(estado)

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

    def _update_offset(self, channel):
        if channel == 1:
            val_str = self.ui.ch1_offset_valor.text()
            unit_str = self.ui.ch1_offset_unidad.currentText()
        else:
            val_str = self.ui.ch2_offset_valor.text()
            unit_str = self.ui.ch2_offset_unidad.currentText()

        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_channel_offset(channel, scale)

    def _update_delay(self):
        val_str = self.ui.delay_valor.text()
        unit_str = self.ui.delay_unidad.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_timebase_position(scale)

    def _update_trigger_level(self):
        val_str = self.ui.trigger_nivel_valor.text()
        unit_str = self.ui.trigger_nivel_unidad.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_trigger_level(scale)

    @Slot(str)
    def _handle_thread_error(self, error_msg):
        self.ui.btn_esperar_onda.setEnabled(True)
        self.ui.btn_esperar_onda.setText("Iniciar")
        QMessageBox.critical(None, "Error de Comunicación", f"Se produjo un error:\n{error_msg}")

    def synchronize_instrument(self):
        if not self.osc.dso:
            return

        # Restablecer instrumento a valores de fábrica.
        self.osc.default_settings()

        # Espera 1500 ms para que procese el reinicio interno.
        QTimer.singleShot(1500, self._continue_synchronization)

    def _continue_synchronization(self):
        if not self.osc.dso:
            return

        # Escala Vertical y Offset.
        self._update_v_scale(1, self.ui.ch1_tension_valor.currentText(), self.ui.ch1_tension_unidad.currentText())
        self._update_offset(1)
        self._update_v_scale(2, self.ui.ch2_tension_valor.currentText(), self.ui.ch2_tension_unidad.currentText())
        self._update_offset(2)

        # Escala Horizontal y Delay.
        self._update_t_scale()
        self._update_delay()

        # Trigger.
        self._update_trigger_level()
        slope = 0 if self.ui.trigger_f_positivo.isChecked() else 1
        self.osc.set_trigger_slope(slope)

        # Habilitar/Deshabilitar canales según el estado inicial de la GUI.
        self.osc.set_channel_display(1, 1 if self.ui.ch1_habilitador.isChecked() else 0)
        self.osc.set_channel_display(2, 1 if self.ui.ch2_habilitador.isChecked() else 0)

    def _change_voltage_unit(self, canal, unidad):
        combo_valor = self.ui.ch1_tension_valor if canal == 1 else self.ui.ch2_tension_valor
        valor_actual = combo_valor.currentText()

        # Bloquear señales temporalmente mientras se vacía y llena la lista.
        combo_valor.blockSignals(True)
        try:
            combo_valor.clear()
            opciones_validas = self.valores_tension.get(unidad, ["1"])
            combo_valor.addItems(opciones_validas)

            # Si el número que estaba seleccionado existe en la nueva unidad, se mantiene.
            if valor_actual in opciones_validas:
                combo_valor.setCurrentText(valor_actual)
        finally:
            combo_valor.blockSignals(False)

        # Enviar la nueva configuración final al osciloscopio
        self._update_v_scale(canal, combo_valor.currentText(), unidad)

    def _change_time_unit(self, unidad):
        combo_valor = self.ui.tiempo_valor
        valor_actual = combo_valor.currentText()
        combo_valor.blockSignals(True)

        try:
            combo_valor.clear()
            opciones_validas = self.valores_tiempo.get(unidad, ["1"])
            combo_valor.addItems(opciones_validas)

            if valor_actual in opciones_validas:
                combo_valor.setCurrentText(valor_actual)

        finally:
            combo_valor.blockSignals(False)

        self._update_t_scale()