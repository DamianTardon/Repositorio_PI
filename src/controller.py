import os
import time
import re
import numpy as np
from PySide6.QtCore import QObject, QThread, Signal, Slot, QRegularExpression, QTimer
from PySide6.QtWidgets import QMessageBox, QFileDialog, QMenu
from PySide6.QtGui import QRegularExpressionValidator, QIntValidator, QFont, QAction
import pyqtgraph as pg

DEBUG_MODE = os.environ.get("DEBUG_MODE", "True") == "True"

class MockChannel2Analyzer:
    """
    Clase contenedora ligera para el CH2. 
    Almacena la onda multiplicada por sus atenuadores para graficar y guardar
    sin calcular los parámetros del impulso (T1, T2, etc.).
    """
    def __init__(self, waveform, dt):
        self.raw_voltage = np.array(waveform)
        self.time_axis = np.arange(len(self.raw_voltage)) * dt
        self.aligned_time_axis = None
        self.test_voltage_curve = self.raw_voltage
        
        # Normalización simple para que la vista 'normalizada' no falle
        max_val = np.max(np.abs(self.test_voltage_curve))
        if max_val != 0:
            self.test_voltage_curve_norm = self.test_voltage_curve / max_val
        else:
            self.test_voltage_curve_norm = self.test_voltage_curve

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
        
        # Ahora almacenan datos múltiples basados en el número de canal activo
        self.pending_analyzers = {}  # { 1: info_ch1, 2: info_ch2 }
        self.last_acquired_data = {} # { 1: (buffer, wave, real_wave, dt), 2: ... }
        
        self.waveform_count = 0
        self.project_created = False    # Bandera de creación de carpeta.

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
            "µs": ["1", "2.5", "5", "10", "25", "50", "100", "250", "500"],
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

        time_units = ["ns", "µs", "ms", "s"]
        self.ui.time_unit.addItems(time_units)
        self.ui.delay_unit.addItems(time_units)

        # Inicializar unidades de medida.
        self.ui.ch1_voltage_value.addItems(self.voltage_values["mV"])
        self.ui.ch2_voltage_value.addItems(self.voltage_values["mV"])
        self.ui.time_value.addItems(self.time_values["µs"])

        # Inicializar valores del osciloscopio.
        self.ui.ch1_offset_value.setText("0.0")
        self.ui.ch2_offset_value.setText("0.0")
        self.ui.delay_value.setText("0.0")
        self.ui.trigger_level_value.setText("0.0")

        # Inicializar atenuaciones.
        self.ui.ch1_resistive_divider_value.setText("1.0")
        self.ui.ch1_attenuator_value.setText("1.0")
        self.ui.ch2_resistive_divider_value.setText("1.0")
        self.ui.ch2_attenuator_value.setText("1.0")

        # Inicializar habilitadores de canales.
        self.ui.ch1_enabler.setChecked(True)
        self.ui.ch2_enabler.setChecked(True)
        self._toggle_attenuations()

        # Configuración inicial del gráfico (pyqtgraph)
        self.ui.graph_view.setBackground('w') # Fondo blanco
        self.ui.graph_view.showGrid(x=True, y=True, alpha=0.3)

        # Variables para acumular ondas en memoria RAM.
        self.saved_waves_data = {}
        self.color_index = 0

        # Asignar Menú al botón creado en Qt Designer.
        self.visibility_menu = QMenu(self.ui.btn_visibility)
        self.ui.btn_visibility.setMenu(self.visibility_menu)

        # Acciones globales para el menú.
        self.action_show_all = QAction("Mostrar todas", self)
        self.action_show_all.triggered.connect(lambda: self._set_all_waves_visibility(True))
        self.visibility_menu.addAction(self.action_show_all)

        self.action_hide_all = QAction("Ocultar todas", self)
        self.action_hide_all.triggered.connect(lambda: self._set_all_waves_visibility(False))
        self.visibility_menu.addAction(self.action_hide_all)

        self.visibility_menu.addSeparator() # Agrega una línea separadora.

        # Definir el color y estilo para los textos.
        text_color = '#000000' # Negro
        label_style = {'color': text_color, 'font-size': '12pt', 'font-weight': 'bold'}

        # Crear la leyenda en la esquina superior derecha, con fondo blanco y borde negro.
        self.legend = self.ui.graph_view.addLegend(
            offset=(10, 10),
            brush=pg.mkBrush(255, 255, 255, 255), # Fondo blanco.
            pen=pg.mkPen(color='k', width=1)      # Borde negro de 1px.
        )
        # Establecer el valor Z para que la leyenda esté por encima de las curvas.
        self.legend.setZValue(10)
        # Configurar la tipografía de la leyenda.
        self.legend.setLabelTextColor(text_color)
        self.legend.setLabelTextSize('11pt')

        # Color de los nombres de los ejes y el título.
        self.ui.graph_view.setLabel('bottom', 'Tiempo', units='s', **label_style)
        self.ui.graph_view.setLabel('left', 'Tensión', units='V', **label_style)
        self.ui.graph_view.setTitle('Esperando captura...', color=text_color, size='14pt')

        # Color de los números (ticks) y la línea del eje.
        axis_pen = pg.mkPen(color=text_color)
        bottom_axis = self.ui.graph_view.getAxis('bottom')
        bottom_axis.setTextPen(axis_pen)
        bottom_axis.setPen(axis_pen)
        bottom_axis.setZValue(-1)

        left_axis = self.ui.graph_view.getAxis('left')
        left_axis.setTextPen(axis_pen)
        left_axis.setPen(axis_pen)
        left_axis.setZValue(-1)

    def _connect_signals(self):
        # Botones principales.
        self.ui.btn_search_instrument.clicked.connect(self.search_manual_instrument)
        self.ui.btn_create_folder.clicked.connect(self.create_new_project)
        self.ui.btn_save_waveform.clicked.connect(self.save_waveform)

        if DEBUG_MODE:
            self.ui.btn_wait_waveform.clicked.connect(self.load_tdg_waveform)
        else:
            self.ui.btn_wait_waveform.clicked.connect(self.receive_waveform)

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

        # Handlers de Variables Continuas (Offset, Delay, Trigger Level).
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

        # Validadores en tiempo real para Atenuaciones y reprocesamiento automático.
        self.ui.ch1_resistive_divider_value.editingFinished.connect(lambda: self._on_attenuation_changed(self.ui.ch1_resistive_divider_value, "Divisor resistivo (CH1)", 1))
        self.ui.ch1_attenuator_value.editingFinished.connect(lambda: self._on_attenuation_changed(self.ui.ch1_attenuator_value, "Atenuador (CH1)", 1))
        self.ui.ch2_resistive_divider_value.editingFinished.connect(lambda: self._on_attenuation_changed(self.ui.ch2_resistive_divider_value, "Divisor resistivo (CH2)", 2))
        self.ui.ch2_attenuator_value.editingFinished.connect(lambda: self._on_attenuation_changed(self.ui.ch2_attenuator_value, "Atenuador (CH2)", 2))

        # Handlers para los Radio Buttons del tipo de gráfico.
        self.ui.normalized_type_radio.toggled.connect(self._on_graph_type_changed)
        self.ui.real_type_radio.toggled.connect(self._on_graph_type_changed)

    def _update_results_gui(self, analyzer):
        results = analyzer.results

        # Función interna para formatear o dejar en blanco los campos de resultados.
        def set_val(line_edit, key, scale=1.0):
            val = results.get(key)
            if val is not None:
                line_edit.setText(f"{val * scale:.2f}")
            else:
                line_edit.setText("") # Deja en blanco si no se pudo calcular

        set_val(self.ui.peak_voltage_value, "Ut", 1/1000.0)
        set_val(self.ui.t1_value, "T1", 1e6)
        set_val(self.ui.t2_value, "T2", 1e6)
        set_val(self.ui.os_value, "Beta_prime", 1.0)

    def _on_graph_type_changed(self):
        # Actualiza el gráfico según lo que elija el usuario: "real" o "normalizado".
        self._update_plot()

    def _update_plot(self):
        # Título del gráfico basado en el número de ítem.
        item_num = self.ui.item_number_value.text().strip()
        item_year = self.ui.item_year_value.text().strip()
        graph_title = f"{item_num}-{item_year}"

        self.ui.graph_view.clear() # Limpia el lienzo en cada actualización.
        text_color = '#000000'
        label_style = {'color': text_color, 'font-size': '12pt', 'font-weight': 'bold'}
        # Bandera para seleccionar datos según el Radio Button activo.
        is_normalized = self.ui.normalized_type_radio.isChecked()

        # Graficar todas las ondas guardadas que estén visibles.
        for name, wave in self.saved_waves_data.items():
            if wave["is_visible"]:
                y_data = wave["y_norm"] if is_normalized else wave["y_real"]
                pen = pg.mkPen(color=wave["color"], width=2)
                self.ui.graph_view.plot(wave["t"], y_data, name=name, pen=pen)

        # Graficar las ondas actuales en el buffer (CH1 y/o CH2).
        has_pending = False
        for ch, info in self.pending_analyzers.items():
            has_pending = True
            analyzer = info["analyzer"]
            is_successful = info["success"]

            # Seleccionar el eje de tiempo adecuado (usa el alineado si existe).
            t_axis = analyzer.aligned_time_axis if analyzer.aligned_time_axis is not None else analyzer.time_axis

            if is_successful:
                y_data = analyzer.test_voltage_curve_norm if is_normalized else analyzer.test_voltage_curve
                if ch == 1:
                    pen_color = (0, 100, 200) # Azul para CH1
                    legend_name = "Actual (CH1)"
                else:
                    pen_color = (0, 150, 0) # Verde oscuro para CH2
                    legend_name = "Actual (CH2)"
            else:
                y_data = analyzer.raw_voltage
                pen_color = (200, 0, 0) # Rojo para error
                legend_name = f"Error (CH{ch})"
            # Dibujar la curva en el lienzo.
            if t_axis is not None and y_data is not None:
                pen = pg.mkPen(color=pen_color, width=3) # Más gruesa para destacar.
                self.ui.graph_view.plot(t_axis, y_data, name=legend_name, pen=pen)

        if has_pending:
            self.ui.graph_view.setTitle("Onda(s) sin guardar", color=text_color, size='14pt', bold=True)
        else:
            self.ui.graph_view.setTitle(graph_title, color=text_color, size='14pt', bold=True)

        # Actualizar etiquetas de ejes.
        if is_normalized:
            self.ui.graph_view.setLabel('left', 'Tensión / Magnitud Normalizada', units='p.u.', **label_style)
        else:
            self.ui.graph_view.setLabel('left', 'Tensión / Magnitud', units='V / A', **label_style)

    def load_tdg_waveform(self):
        # Abrir explorador de archivos.
        file_path, _ = QFileDialog.getOpenFileName(
            None,
             "Seleccionar onda de calibración (TDG)",
             "",
             "Archivos de texto (*.txt *.dat *.csv);;Todos los archivos (*)"
        )
        if not file_path:
            return # El usuario cerró la ventana sin elegir nada.

        try:
            # Leer el archivo usando la función de file_manager.py
            metadata, data_list = self.fm.read_TDG_file(file_path)
            # Extraer dt y convertir la lista de tensión a un array de NumPy.
            dt = metadata['sampling_period']
            waveform = np.array(data_list)
            # Crear un inBuffer ficticio para que no falle al probar el botón de Guardar.
            inBuffer = b'DATOS_DE_CALIBRACION_TDG'

            # Simula leer en el canal principal activo.
            active_channel = 1 if self.ui.ch1_enabler.isChecked() else (2 if self.ui.ch2_enabler.isChecked() else 1)
            real_waveform = self._apply_hardware_attenuations(waveform, active_channel)

            self.last_acquired_data = {}
            self.last_acquired_data[active_channel] = (inBuffer, waveform, real_waveform, dt)

            self._process_and_plot_acquired_data()

        except Exception as e:
            QMessageBox.critical(None, "Error de Lectura", f"No se pudo cargar el archivo:\n{str(e)}")

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

        # Validar que ningún campos esté vacío.
        if not item_num or not item_year:
            QMessageBox.warning(
                None,
                "Datos faltantes",
                "Por favor, complete el campo 'Item' para crear la carpeta del ensayo."
            )
            return

        # Verificar los textos para evitar caracteres inválidos en rutas de Windows/Linux.
        item_num = re.sub(r'[\\/*?:"<>|]', "", item_num)
        item_year = re.sub(r'[\\/*?:"<>|]', "", item_year)
        client = re.sub(r'[\\/*?:"<>|]', "", client)

        # Si los datos están completos, crea el nombre de la carpeta.
        folder_name = f"{item_num}-{item_year}"
        # Si el campo cliente está completo, lo agrega al nombre de la carpeta.
        if client:
            folder_name += f" - {client}"

        # Abrir explorador de carpetas.
        base_dir = QFileDialog.getExistingDirectory(
            None,
            "Seleccionar ubicación para el nuevo ensayo",
            "",  # Inicia en el último directorio usado.
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        
        # Si el usuario cierra la ventana o presiona cancelar, aborta la operación.
        if not base_dir:
            return

        # Validación de carpeta existente.
        full_path = os.path.join(base_dir, folder_name)
        if os.path.exists(full_path):
            QMessageBox.warning(
                None,
                "Carpeta Existente",
                f"La carpeta '{folder_name}' ya existe.\n"
                f"Elija otra ubicación.")
            return

        # Crear la estructura en el directorio seleccionado por el usuario.
        self.fm.create_new_structure(folder_name, base_dir=base_dir)

        # Reiniciar memoria del ensayo.
        self.ref_analyzer = None
        self.waveform_count = 0
        self.ui.graph_name.setText("Ensayo inicializado")
        self.project_created = True # Habilita el guardado de ondas.

        # Normalizar las barras invertidas para que se lea mejor en Windows.
        full_path_display = os.path.normpath(full_path)
        QMessageBox.information(None, "Éxito", f"Carpeta creada correctamente en:\n\n{full_path_display}")

    def receive_waveform(self):
        if not self.osc.dso:
            QMessageBox.warning(None, "Error", "El osciloscopio no está conectado.")
            return

        # Si el hilo ya está corriendo, el botón actúa como "Cancelar".
        if self.wait_thread and self.wait_thread.isRunning():
            self.wait_thread.stop()
            self.ui.btn_wait_waveform.setText("Iniciar")
            return

        # Configurar estado de espera.
        self.ui.btn_wait_waveform.setText("Cancelar")
        self.wait_thread = WaitWaveformThread(self.osc)
        self.wait_thread.wave_detected.connect(self.process_waveform)
        self.wait_thread.error_occurred.connect(self._handle_thread_error)
        # Restaura el botón de captura de onda, luego de la cancelación.
        self.wait_thread.finished.connect(lambda: self.ui.btn_wait_waveform.setText("Iniciar"))
        self.wait_thread.start()

    @Slot()
    def process_waveform(self):
        self.ui.btn_wait_waveform.setEnabled(True)
        self.ui.btn_wait_waveform.setText("Iniciar")

        # Determinar los canales activos.
        ch1_active = self.ui.ch1_enabler.isChecked()
        ch2_active = self.ui.ch2_enabler.isChecked()

        if not ch1_active and not ch2_active:
            QMessageBox.warning(None, "Cuidado", "Se detectó disparo, pero no hay canales habilitados para leer.")
            return

        self.last_acquired_data = {}

        # Capturar ambos canales si están activos.
        if ch1_active:
            inBuffer, waveform, dt = self.osc.get_block_data(1)
            # Invertir atenuaciones del sistema para determinar el valor real de la onda.
            # Guardar temporalmente hasta que el usuario accione el botón Guardar.
            if waveform is not None:
                real_waveform = self._apply_hardware_attenuations(waveform, 1)
                self.last_acquired_data[1] = (inBuffer, waveform, real_waveform, dt)
        if ch2_active:
            inBuffer, waveform, dt = self.osc.get_block_data(2)
            if waveform is not None:
                real_waveform = self._apply_hardware_attenuations(waveform, 2)
                self.last_acquired_data[2] = (inBuffer, waveform, real_waveform, dt)

        self._process_and_plot_acquired_data()

    def _process_and_plot_acquired_data(self):
        self.pending_analyzers = {}
        
        ch1_active = 1 in self.last_acquired_data
        ch2_active = 2 in self.last_acquired_data

        if ch1_active:
            _, _, real_waveform, dt = self.last_acquired_data[1]
            temp_analyzer = self.AnalyzerClass(real_waveform, dt, sigma_fit=1.0)
            try:
                if self.ref_analyzer is None:
                    temp_analyzer.ref_lightning_impulse()
                else:
                    temp_analyzer.lightning_impulse(self.ref_analyzer)
                
                # Procesó la onda exitosamente.
                # Guardar el analizador exitoso y actualiza la GUI.
                self._update_results_gui(temp_analyzer)
                self.pending_analyzers[1] = {"analyzer": temp_analyzer, "success": True}

            except ValueError as e:
                # Ocurrió algún problema al procesar la onda.
                # Capturar errores de análisis (Onda corta, ruido, etc.).
                # Actualiza los valores parciales calculados.
                # Indica que falló la matemática.
                self._update_results_gui(temp_analyzer)
                self.pending_analyzers[1] = {"analyzer": temp_analyzer, "success": False}
                QMessageBox.warning(None, "Advertencia de Análisis CH1", str(e))

            except Exception as e:
                # Captura y muestra fallos críticos inesperados.
                self._update_results_gui(temp_analyzer)
                self.pending_analyzers[1] = {"analyzer": temp_analyzer, "success": False}
                QMessageBox.critical(
                    None,
                    "Error Crítico de Análisis CH1",
                    "Ocurrió un error inesperado al calcular los parámetros de la onda."
                )

        else:
            # Si CH1 no corrió, limpiamos el panel de resultados
            self.ui.peak_voltage_value.setText("")
            self.ui.t1_value.setText("")
            self.ui.t2_value.setText("")
            self.ui.os_value.setText("")

        if ch2_active:
            _, _, real_waveform, dt = self.last_acquired_data[2]
            # CH2 no hace matemática, solo es un contenedor adaptado para graficar
            temp_analyzer2 = MockChannel2Analyzer(real_waveform, dt)
            self.pending_analyzers[2] = {"analyzer": temp_analyzer2, "success": True}

        self._update_plot()

    def save_waveform(self):
        # Validar que la carpeta exista antes de guardar la onda.
        if not self.project_created:
            QMessageBox.warning(
                None, 
                "Acción no permitida", 
                "Debe completar los Datos del ensayo y Crear la Carpeta\n para poder guardar los resultados."
            )
            return

        # Validar Condiciones Ambientales.
        t_bs = self.ui.db_temperature_value.text().strip()
        t_bh = self.ui.wb_temperature_value.text().strip()
        hr = self.ui.relative_humidity_value.text().strip()
        ha = self.ui.absolute_humidity_value.text().strip()
        pres = self.ui.pressure_value.text().strip()

        # all() verifica que ninguna de las cadenas de texto esté vacía ("").
        if not all([t_bs, t_bh, hr, ha, pres]):
            QMessageBox.warning(None, "Condiciones Incompletas", "Complete todos los campos de las 'Condiciones ambientales' antes de guardar.")
            return

        # Validar que haya datos capturados para guardar.
        if not self.last_acquired_data:
            QMessageBox.warning(None, "Aviso", "No hay ninguna onda adquirida en memoria para guardar.")
            return

        ch1_active = 1 in self.last_acquired_data
        ch2_active = 2 in self.last_acquired_data
        both_active = ch1_active and ch2_active

        # Definir nombre de la onda.
        if self.waveform_count == 0:
            base_name_str = "Referencia"
        else:
            base_name_str = f"Onda_{self.waveform_count:02d}"

        self.waveform_count += 1
        saved_names = []

        if ch1_active:
            name_ch1 = f"{base_name_str}_V" if both_active else base_name_str
            self._save_single_channel(1, name_ch1)
            saved_names.append(name_ch1)

        if ch2_active:
            name_ch2 = f"{base_name_str}_A" if both_active else base_name_str
            self._save_single_channel(2, name_ch2)
            saved_names.append(name_ch2)

        self.ui.graph_name.setText(" / ".join(saved_names))
        QMessageBox.information(None, "Guardado", f"{', '.join(saved_names)} guardada(s) exitosamente.")

        # Limpiar
        self.last_acquired_data = {}
        self.pending_analyzers = {}
        self._update_plot()

    def _save_single_channel(self, channel, save_name):
        inBuffer, waveform, real_waveform, dt = self.last_acquired_data[channel]
        analyzer_info = self.pending_analyzers.get(channel)

        bin_path = self.fm.get_new_name(prefijo=save_name, extension=".bin")
        self.fm.create_bin_int16(inBuffer, bin_path)

        if analyzer_info and analyzer_info["success"]:
            analyzer = analyzer_info["analyzer"]

            if channel == 1 and self.waveform_count == 1:
                self.ref_analyzer = analyzer

            # Guardar toda la información de la onda.
            h5_path = self.fm.get_new_name(prefijo=save_name, extension=".h5")
            self.fm.create_hdf5(analyzer.time_axis, analyzer.raw_voltage, h5_path)

            # Guardar resultados del análisis.
            csv_path = self.fm.get_new_name(prefijo=save_name, extension=".csv")
            self.fm.create_csv(analyzer.time_axis, analyzer.raw_voltage, csv_path)

            color = pg.intColor(self.color_index, hues=15, maxValue=200)
            self.color_index += 1

            t_data = analyzer.aligned_time_axis if analyzer.aligned_time_axis is not None else analyzer.time_axis

            self.saved_waves_data[save_name] = {
                "t": t_data,
                "y_real": analyzer.test_voltage_curve,
                "y_norm": analyzer.test_voltage_curve_norm,
                "color": color,
                "is_visible": True
            }

            # Agregar el checkbox al menú desplegable.
            action = QAction(save_name, self)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(lambda checked, n=save_name: self._toggle_wave_visibility(n, checked))
            self.visibility_menu.addAction(action)

        else:
            QMessageBox.warning(
                None,
                "Análisis Fallido",
                f"El respaldo original de {save_name} se guardó como .bin\n",
                f"Pero no se generaron archivos de análisis, ni de resultados."
            )

    def _apply_hardware_attenuations(self, waveform, channel):
        if channel == 1:
            divider = float(self.ui.ch1_resistive_divider_value.text())
            attenuator = float(self.ui.ch1_attenuator_value.text())
        else:
            divider = float(self.ui.ch2_resistive_divider_value.text())
            attenuator = float(self.ui.ch2_attenuator_value.text())

        return waveform * divider * attenuator

    def _check_attenuation_value(self, line_edit, field_name):
        text = line_edit.text().strip()
        # Si el campo está vacío. Se asigna por defecto: 1.0.
        if not text:
            line_edit.setText("1.0")
            return
        try:
            val = float(text)
            if val <= 0:
                QMessageBox.warning(None, "Valor Inválido", f"El valor en '{field_name}' debe ser mayor a 0.\nSe restaurará a 1.0.")
                line_edit.setText("1.0")
        except ValueError:
            QMessageBox.warning(None, "Valor Inválido", f"El valor en '{field_name}' no es reconocido.\nSe restaurará a 1.0.")
            line_edit.setText("1.0")

    def _on_attenuation_changed(self, line_edit, field_name, channel):
        # Valida que el texto ingresado sea correcto.
        self._check_attenuation_value(line_edit, field_name)

        # Si hay una onda guardada en la memoria temporal, la reprocesa inmediatamente.
        if channel in self.last_acquired_data:
            inBuffer, waveform, _, dt = self.last_acquired_data[channel]
            real_waveform = self._apply_hardware_attenuations(waveform, channel)
            self.last_acquired_data[channel] = (inBuffer, waveform, real_waveform, dt)

            # Reprocesa y grafica con el nuevo factor.
            self._process_and_plot_acquired_data()

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

    def _toggle_wave_visibility(self, name, checked):
        if name in self.saved_waves_data:
            self.saved_waves_data[name]["is_visible"] = checked
            # Refresca el gráfico manteniendo la onda actual si existe.
            self._update_plot()

    def _set_all_waves_visibility(self, visible):
        # Actualizar el estado de visibilidad de las odas.
        for name in self.saved_waves_data:
            self.saved_waves_data[name]["is_visible"] = visible
        # Sincronizar visualmente los tildes en el menú.
        for action in self.visibility_menu.actions():
            if action.isCheckable():
                # Bloquear señales temporalmente para que no redibuje por cada item.
                action.blockSignals(True)
                action.setChecked(visible)
                action.blockSignals(False)
        self._update_plot()