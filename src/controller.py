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
        self.waveform_count = 0

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
        int_validator = QIntValidator(0, 9999)
        # Decimal positivo.
        pos_dec_regex = QRegularExpression(r"^[0-9]+(\.[0-9]+)?$")
        pos_dec_validator = QRegularExpressionValidator(pos_dec_regex)
        # Decimal negativo/positivo. ("-?" significa guion opcional)
        signed_dec_regex = QRegularExpression(r"^-?[0-9]+(\.[0-9]+)?$")
        signed_dec_validator = QRegularExpressionValidator(signed_dec_regex)

        # Aplicar a Condiciones Ambientales.
        self.ui.db_temperature_value.setValidator(pos_dec_validator)
        self.ui.wb_temperature_value.setValidator(pos_dec_validator)
        self.ui.relative_humidity_value.setValidator(pos_dec_validator)
        self.ui.absolute_humidity_value.setValidator(pos_dec_validator)
        self.ui.pressure_value.setValidator(pos_dec_validator)

        # Aplicar a Atenuaciones del Sistema (Siempre positivos).
        self.ui.ch1_resistive_divider_value.setValidator(pos_dec_validator)
        self.ui.ch1_attenuator_value.setValidator(pos_dec_validator)
        self.ui.ch2_resistive_divider_value.setValidator(pos_dec_validator)
        self.ui.ch2_attenuator_value.setValidator(pos_dec_validator)

        # Aplicar a Offset, delay y nivel de trigger (Pueden ser negativos).
        self.ui.ch1_offset_value.setValidator(signed_dec_validator)
        self.ui.ch2_offset_value.setValidator(signed_dec_validator)
        self.ui.delay_value.setValidator(signed_dec_validator)
        self.ui.trigger_level_value.setValidator(signed_dec_validator)

        # Inicializar las listas desplegables.
        self.voltage_values = {
            "mV": ["2", "5", "10", "20", "50", "100", "200", "500"],
            "V": ["1", "2", "5", "10"]
        }
        self.time_values = {
            "ns": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
            "us": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
            "ms": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
            "s": ["1", "2.5", "5", "10", "25", "50"]
        }

        # Cargar unidades en las listas desplegables.
        voltage_units = ["mV", "V"]
        self.ui.ch1_voltage_unit.addItems(voltage_units)
        self.ui.ch2_voltage_unit.addItems(voltage_units)
        self.ui.ch1_offset_unit.addItems(voltage_units)
        self.ui.ch2_offset_unit.addItems(voltage_units)
        self.ui.trigger_level_unit.addItems(voltage_units)

        time_units = ["ns", "us", "ms", "s"]
        self.ui.time_unit.addItems(time_units)
        self.ui.delay_unit.addItems(time_units)

        # Cargar los valores por defecto.
        self.ui.ch1_voltage_value.addItems(self.voltage_values["mV"])
        self.ui.ch2_voltage_value.addItems(self.voltage_values["mV"])
        self.ui.time_value.addItems(self.time_values["us"])

        # Cargar los textos por defecto.
        self.ui.ch1_offset_value.setText("0.0")
        self.ui.ch2_offset_value.setText("0.0")
        self.ui.delay_value.setText("0.0")
        self.ui.trigger_level_value.setText("0.0")

        # Estado inicial de habilitadores.
        self.ui.ch1_enabler.setChecked(True)
        self.ui.ch2_enabler.setChecked(True)
        self._toggle_attenuations()

    def _connect_signals(self):
        # Botones principales.
        self.ui.btn_search_instrument.clicked.connect(self.search_manual_instrument)
        self.ui.btn_create_folder.clicked.connect(self.create_new_project)
        self.ui.btn_wait_waveform.clicked.connect(self.receive_waveform)
        self.ui.btn_save_waveform.clicked.connect(self.save_waveform)

        # Habilitadores.
        self.ui.attenuations_enabler.stateChanged.connect(self._toggle_attenuations)

        # Handlers de Escala Vertical.
        self.ui.ch1_voltage_value.currentTextChanged.connect(lambda v: self._update_v_scale(1, v, self.ui.ch1_voltage_unit.currentText()))
        self.ui.ch1_voltage_unit.currentTextChanged.connect(lambda u: self._change_voltage_unit(1, u))

        self.ui.ch2_voltage_value.currentTextChanged.connect(lambda v: self._update_v_scale(2, v, self.ui.ch2_voltage_unit.currentText()))
        self.ui.ch2_voltage_unit.currentTextChanged.connect(lambda u: self._change_voltage_unit(2, u))

        # Handler de Escala Horizontal.
        self.ui.time_value.currentTextChanged.connect(self._update_t_scale)
        self.ui.time_unit.currentTextChanged.connect(self._change_time_unit)

        # Handlers de Variables Continuas (Sensibles a valor y unidad).
        self.ui.ch1_offset_value.editingFinished.connect(lambda: self._update_offset(1))
        self.ui.ch1_offset_unit.currentTextChanged.connect(lambda: self._update_offset(1))

        self.ui.ch2_offset_value.editingFinished.connect(lambda: self._update_offset(2))
        self.ui.ch2_offset_unit.currentTextChanged.connect(lambda: self._update_offset(2))

        self.ui.delay_value.editingFinished.connect(self._update_delay)
        self.ui.delay_unit.currentTextChanged.connect(self._update_delay)

        self.ui.trigger_level_value.editingFinished.connect(self._update_trigger_level)
        self.ui.trigger_level_unit.currentTextChanged.connect(self._update_trigger_level)

        # Flanco de Trigger.
        self.ui.trigger_edge_positive.toggled.connect(lambda checked: self.osc.set_trigger_slope(0) if checked else None)
        self.ui.trigger_edge_negative.toggled.connect(lambda checked: self.osc.set_trigger_slope(1) if checked else None)

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
            found_instruments = self.osc.rm.list_resources()
        except Exception as e:
            QMessageBox.critical(None, "Error del Sistema", f"No se pudieron escanear los puertos:\n{e}")
            return

        # Conectar al primer equipo que encuentre.
        if found_instruments:
            port = found_instruments[0]
            self.osc.connect(port)

            # Verificar el estado de la conexión.
            if self.osc.dso is not None:
                self.synchronize_instrument()
                QMessageBox.information(None, "Conexión Exitosa", f"Instrumento enlazado correctamente en el puerto:\n{port}")
            else:
                QMessageBox.warning(None, "Error de Comunicación", f"Se detectó un dispositivo en {port}, pero rechazó la conexión.")
        else:
            QMessageBox.warning(None, "Instrumento no encontrado", "No se detectó hardware conectado a la PC.\nRevise el cable USB y asegúrese de que el osciloscopio esté encendido.")

    def create_new_project(self):
        # Extraer y limpiar los textos ingresados.
        item_num = self.ui.item_number_value.text().strip()
        item_year = self.ui.item_year_value.text().strip()
        client = self.ui.client_value.text().strip()

        # Validar que ninguno de los campos esté vacío.
        if not item_num or not item_year:
            QMessageBox.warning(
                None, 
                "Datos faltantes", 
                "Por favor, complete el campo de 'Item N.°'para crear la carpeta del ensayo."
            )
            return

        # Si los datos están completos, procede con la creación.
        folder_name = f"{item_num}-{item_year}"
        if client:
            folder_name += f" - {client}"

        self.fm.create_new_structure(folder_name)

        # Reiniciar memoria del ensayo.
        self.ref_analyzer = None
        self.waveform_count = 0
        self.ui.graph_name.setText("Proyecto inicializado")
        QMessageBox.information(None, "Éxito", f"Carpeta creada:\n{folder_name}")

    def receive_waveform(self):
        if not self.osc.dso:
            QMessageBox.warning(None, "Error", "El osciloscopio no está conectado.")
            return

        self.ui.btn_wait_waveform.setEnabled(False)
        self.ui.btn_wait_waveform.setText("Esperando...")

        self.wait_thread = WaitWaveformThread(self.osc)
        self.wait_thread.wave_detected.connect(self.process_waveform)
        self.wait_thread.error_occurred.connect(self._handle_thread_error)
        self.wait_thread.start()

    @Slot()
    def process_waveform(self):
        self.ui.btn_wait_waveform.setEnabled(True)
        self.ui.btn_wait_waveform.setText("Iniciar")

        # Determinar canal activo principal.
        active_channel = 1 if self.ui.ch1_enabler.isChecked() else (2 if self.ui.ch2_enabler.isChecked() else None)

        if active_channel is None:
            QMessageBox.warning(None, "Cuidado", "Se detectó disparo, pero no hay canales habilitados para leer.")
            return

        # Descargar bloque de datos.
        inBuffer, waveform, dt = self.osc.get_block_data(active_channel)
        if waveform is None:
            return

        # Guardar temporalmente hasta que el usuario accione el botón Guardar.
        self.last_acquired_data = (inBuffer, waveform, dt)

        # Invertir atenuaciones del sistema para determinar el valor real de la onda.
        real_waveform = self._apply_hardware_attenuations(waveform, active_channel)

        # Instanciar analizador para mostrar valores.
        temp_analyzer = self.AnalyzerClass(real_waveform, dt, sigma_fit=1.0)
        
        try:
            if self.ref_analyzer is None:
                temp_analyzer.ref_lightning_impulse()
            else:
                temp_analyzer.lightning_impulse(self.ref_analyzer)

            # Actualizar GUI con resultados.
            results = temp_analyzer.results
            self.ui.peak_voltage_value.setText(f"{results['Ut']/1000:.2f}") # kV.
            self.ui.t1_value.setText(f"{results['T1']*1e6:.2f}") # us.
            self.ui.t2_value.setText(f"{results['T2']*1e6:.2f}") # us.
            self.ui.os_value.setText(f"{results['Beta_prime']:.2f}") # %

            # TODO: Aquí irá el código de actualización del gráfico (self.ui.graph_view)
            print("Onda procesada y lista para ser guardada.")

        except Exception as e:
            QMessageBox.critical(None, "Error de Análisis", str(e))

    def save_waveform(self):
        if not self.last_acquired_data:
            QMessageBox.warning(None, "Aviso", "No hay ninguna onda adquirida en memoria para guardar.")
            return

        inBuffer, waveform, dt = self.last_acquired_data
        active_channel = 1 if self.ui.ch1_enabler.isChecked() else 2

        self.waveform_count += 1
        base_name = f"Onda_{self.waveform_count:02d}"

        # Guardar Archivos.
        bin_path = self.fm.get_new_name(prefijo=base_name, extension=".bin")
        self.fm.create_bin_int16(inBuffer, bin_path)

        # Analizar en profundidad para fijar estado
        real_waveform = self._apply_hardware_attenuations(waveform, active_channel)
        analyzer = self.AnalyzerClass(real_waveform, dt, sigma_fit=1.0)

        if self.ref_analyzer is None:
            analyzer.ref_lightning_impulse()
            self.ref_analyzer = analyzer
            waveform_type = "Referencia"
        else:
            analyzer.lightning_impulse(self.ref_analyzer)
            waveform_type = "Ensayo"

        # Exportar a HDF5 (Usando el time_axis generado por el analyzer).
        h5_path = self.fm.get_new_name(prefijo=base_name, extension=".h5")
        self.fm.create_hdf5(analyzer.time_axis, real_waveform, h5_path)

        # Actualizar Interfaz.
        self.ui.graph_name.setText(f"{base_name} ({waveform_type})")

        # Limpiar buffer temporal.
        self.last_acquired_data = None
        QMessageBox.information(None, "Guardado", f"{base_name} guardada exitosamente.")

    # --- Utilidades y Actualizadores de Hardware ---

    def _apply_hardware_attenuations(self, waveform, channel):
        try:
            if channel == 1:
                divider = float(self.ui.ch1_resistive_divider_value.text() or 1.0)
                attenuator = float(self.ui.ch1_attenuator_value.text() or 1.0)
            else:
                divider = float(self.ui.ch2_resistive_divider_value.text() or 1.0)
                attenuator = float(self.ui.ch2_attenuator_value.text() or 1.0)

            return waveform * divider * attenuator

        except ValueError:
            return waveform

    def _toggle_attenuations(self):
        state = self.ui.attenuations_enabler.isChecked()
        self.ui.ch1_resistive_divider_value.setEnabled(state)
        self.ui.ch1_attenuator_value.setEnabled(state)
        self.ui.ch2_resistive_divider_value.setEnabled(state)
        self.ui.ch2_attenuator_value.setEnabled(state)

    def _update_v_scale(self, channel, val_str, unit_str):
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_channel_scale(channel, scale)

    def _update_t_scale(self, *args):
        val_str = self.ui.time_value.currentText()
        unit_str = self.ui.time_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_timebase_scale(scale)

    def _update_offset(self, channel):
        if channel == 1:
            val_str = self.ui.ch1_offset_value.text()
            unit_str = self.ui.ch1_offset_unit.currentText()
        else:
            val_str = self.ui.ch2_offset_value.text()
            unit_str = self.ui.ch2_offset_unit.currentText()

        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_channel_offset(channel, scale)

    def _update_delay(self):
        val_str = self.ui.delay_value.text()
        unit_str = self.ui.delay_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_timebase_position(scale)

    def _update_trigger_level(self):
        val_str = self.ui.trigger_level_value.text()
        unit_str = self.ui.trigger_level_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_trigger_level(scale)

    @Slot(str)
    def _handle_thread_error(self, error_msg):
        self.ui.btn_wait_waveform.setEnabled(True)
        self.ui.btn_wait_waveform.setText("Iniciar")
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
        self._update_v_scale(1, self.ui.ch1_voltage_value.currentText(), self.ui.ch1_voltage_unit.currentText())
        self._update_offset(1)
        self._update_v_scale(2, self.ui.ch2_voltage_value.currentText(), self.ui.ch2_voltage_unit.currentText())
        self._update_offset(2)

        # Escala Horizontal y Delay.
        self._update_t_scale()
        self._update_delay()

        # Trigger.
        self._update_trigger_level()
        slope = 0 if self.ui.trigger_edge_positive.isChecked() else 1
        self.osc.set_trigger_slope(slope)

        # Habilitar/Deshabilitar canales según el estado inicial de la GUI.
        self.osc.set_channel_display(1, 1 if self.ui.ch1_enabler.isChecked() else 0)
        self.osc.set_channel_display(2, 1 if self.ui.ch2_enabler.isChecked() else 0)

    def _change_voltage_unit(self, channel, unit):
        value_selector = self.ui.ch1_voltage_value if channel == 1 else self.ui.ch2_voltage_value
        current_value = value_selector.currentText()

        # Bloquear señales temporalmente mientras vaciamos y llena la lista.
        value_selector.blockSignals(True)
        try:
            value_selector.clear()
            valid_options = self.voltage_values.get(unit, ["1"])
            value_selector.addItems(valid_options)

            # Si el número que estaba seleccionado existe en la nueva unidad, se mantiene.
            if current_value in valid_options:
                value_selector.setCurrentText(current_value)
        finally:
            value_selector.blockSignals(False)

        # Enviar la nueva configuración final al osciloscopio
        self._update_v_scale(channel, value_selector.currentText(), unit)

    def _change_time_unit(self, unit):
        value_selector = self.ui.time_value
        current_value = value_selector.currentText()
        value_selector.blockSignals(True)

        try:
            value_selector.clear()
            valid_options = self.time_values.get(unit, ["1"])
            value_selector.addItems(valid_options)

            if current_value in valid_options:
                value_selector.setCurrentText(current_value)

        finally:
            value_selector.blockSignals(False)

        self._update_t_scale()