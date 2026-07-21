r"""Módulo de acoplamiento lógico y presentación MVP 
(Modelo-Vista-Presentador).

Gobierna las interacciones síncronas/asíncronas generadas desde los 
elementos visuales de la GUI de PySide6, el envío dinámico de comandos 
de control al osciloscopio y las subrutinas de cómputo.
"""

from __future__ import annotations

import os
import time
import re
import numpy as np
import platform
import subprocess
import pyqtgraph as pg
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog, QMenu, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator, QIntValidator, QAction
from PySide6.QtCore import (
    QObject, QRegularExpression, QThread, QTimer, Qt, Signal, Slot,
)


# Importaciones exclusivas para el tipado estático en la documentación.
from typing import Union, Dict, Any, Optional, Tuple, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ui_graphic_user_interface import Ui_MainWindow
    from gw_instek_gds1000a_u import GWInstekGDS1000AU
    from file_manager import FileManager
    from impulse_analyzer import LightningImpulseAnalyzer

DEBUG_MODE: bool = os.environ.get("DEBUG_MODE", "False") == "True"
#DEBUG_MODE: bool = False
r"""Bandera global de habilitación de depuración de componentes lógicos 
de captura.
"""

class MockChannel2Analyzer:
    r"""Contenedor de datos pasivo para la señal del canal 2 (corriente).

    Almacena la onda escalada por sus atenuadores para tareas de 
    visualización y persistencia.
    Omite el cálculo de parámetros normativos (:math:`T_1`, :math:`T_2`, 
    etc.) al no ser aplicables a esta magnitud física en el contexto del 
    analizador principal.

    Attributes:
        raw_voltage (np.ndarray): Array crudo de corriente registrado.
        time_axis (np.ndarray): Vector de tiempo base del impulso.
        aligned_time_axis (Optional[np.ndarray]): Vector de tiempo 
            alineado para sincronización en gráficos.
        test_voltage_curve (np.ndarray): Curva de corriente real 
            escalada por atenuadores.
        test_voltage_curve_norm (np.ndarray): Curva de corriente 
            normalizada a :math:`\qty{1.0}{\text{p.u.}}`.
    """

    def __init__(
            self, 
            waveform: Union[list, np.ndarray], 
            dt: float
    ) -> None:
        r"""Inicializa el contenedor y normaliza la onda para su 
        graficación.

        .. note::
            Implementa una medida de seguridad (fail-safe) durante la 
            normalización: verifica que el valor máximo absoluto de la 
            curva sea distinto de cero (``max_val != 0``). Esto previene 
            una excepción crítica por división por cero si el hardware 
            captura una señal completamente nula (plana).

        Args:
            waveform (Union[list, np.ndarray]): Datos crudos del canal 2.
            dt (float): Periodo de muestreo del instrumento en 
                :math:`\unit{\second}`.
        """
        self.raw_voltage = np.array(waveform)
        self.time_axis = np.arange(len(self.raw_voltage)) * dt
        self.aligned_time_axis = None
        self.test_voltage_curve = self.raw_voltage

        # Normalización simple para que la vista 'normalizada' no falle.
        max_val = np.max(np.abs(self.test_voltage_curve))
        if max_val != 0:
            self.test_voltage_curve_norm = self.test_voltage_curve / max_val
        else:
            self.test_voltage_curve_norm = self.test_voltage_curve

class WaitWaveformThread(QThread):
    r"""Hilo trabajador (Worker Thread) para el monitoreo de adquisición 
    de hardware.

    Gestiona el bucle de espera del estado de disparo (trigger) del 
    osciloscopio en segundo plano para evitar el bloqueo del hilo 
    principal (GUI thread).

    Attributes:
        wave_detected (Signal): Señal emitida cuando el estado del 
            instrumento es 'Disparado'.
        error_occurred (Signal): Señal emitida con la traza del error en 
            caso de fallo de hardware.
        oscilloscope (GWInstekGDS1000AU): Instancia del controlador del 
            instrumento.
        _is_running (bool): Bandera interna que controla la permanencia 
            en el bucle de sondeo.
    """
    wave_detected = Signal()
    error_occurred = Signal(str)

    def __init__(self, oscilloscope: GWInstekGDS1000AU) -> None:
        r"""Inicializa el hilo con la referencia al osciloscopio.

        Args:
            oscilloscope (GWInstekGDS1000AU): Instancia del manejador de 
                comunicación VISA del equipo.
        """
        super().__init__()
        self.oscilloscope = oscilloscope
        self._is_running = True

    def run(self) -> None:
        r"""Ejecuta el bucle de sondeo (polling) del estado del trigger.

        Arma el disparo único en el hardware y consulta repetitivamente 
        el estado de captura. Si ocurre una falla en el bus o 
        comunicación, atrapa la excepción y emite la señal de error.

        .. note::
            El bucle de sondeo incorpora una pausa de 
            :math:`\qty{200}{\milli\second}` (``time.sleep(0.2)``) por 
            cada iteración. Esto es vital para evitar que el hilo 
            consuma recursos innecesarios del procesador (CPU) mientras 
            espera el evento físico en el instrumento.
        """
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

    def stop(self) -> None:
        r"""Interrumpe el bucle de sondeo modificando la bandera de 
        control de forma segura."""
        self._is_running = False

class MainPresenter(QObject):
    r"""Presentador principal del patrón Modelo-Vista-Presentador (MVP).

    Orquesta la interacción entre la Vista (interfaz gráfica) y el Modelo 
    (el hardware de adquisición y el motor matemático/almacenamiento). 
    Maneja la lógica de presentación, estados de ensayos y renderizado 
    de gráficos a través de pyqtgraph.

    Attributes:
        ui (Ui_MainWindow): Interfaz de usuario generada e instanciada.
        osc (GWInstekGDS1000AU): Controlador del hardware (osciloscopio).
        fm (FileManager): Gestor de archivos y base de datos HDF5.
        AnalyzerClass (Type[LightningImpulseAnalyzer]): Referencia 
            inyectada a la clase analizadora matemática.
        ref_analyzer (Optional[LightningImpulseAnalyzer]): Instancia de 
            analizador para el impulso pleno de referencia.
        pending_analyzers (Dict[int, Dict[str, Any]]): Buffer de 
            analizadores recién adquiridos sin guardar.
        last_acquired_data (Dict[int, Tuple[Any, np.ndarray, np.ndarray, float]]): 
            Buffer crudo con las tuplas 
            `(inBuffer, waveform, real_waveform, dt)` 
            recién adquiridas por canal.
        wave_count (int): Contador de impulsos de ensayo procesados.
        ref_count (int): Contador de impulsos de referencia procesados.
        project_created (bool): Bandera de estado que habilita el 
            almacenamiento de resultados.
        wait_thread (Optional[WaitWaveformThread]): Referencia al hilo 
            de adquisición asíncrona.
        saved_waves_data (Dict[str, Any]): Buffer en RAM de las ondas 
            cargadas/guardadas para renderizado.
        color_index (int): Índice que controla la rotación de 
            tonalidades para las ondas dibujadas.
        voltage_values (Dict[str, list[str]]): Valores permitidos de la 
            escala de amplitud (V/div) según la magnitud seleccionada.
        time_values (Dict[str, list[str]]): Valores permitidos de la 
            escala de tiempo (s/div) según la magnitud.
        visibility_menu (QMenu): Menú contextual para el control de 
            visibilidad de trazas.
        action_show_all (QAction): Puntero al botón de menú para 
            habilitar visibilidad de todas las ondas almacenadas.
        action_hide_all (QAction): Puntero al botón de menú para 
            deshabilitar visibilidad de todas las ondas almacenadas.
        legend (pg.LegendItem): Leyenda principal del lienzo de ploteo 
            de PyQtGraph.
        view_box_ch2 (pg.ViewBox): Caja de vista superpuesta para 
            escalar independientemente el CH2.
        right_axis (pg.AxisItem): Eje Y secundario anclado a la derecha 
            para magnitud de corriente.
    """

    def __init__(
            self, 
            ui: Ui_MainWindow, 
            oscilloscope: GWInstekGDS1000AU, 
            file_manager: FileManager, 
            analyzer_class: Type[LightningImpulseAnalyzer]
    ) -> None:
        r"""Inyecta las dependencias del sistema e inicializa el estado 
        dinámico del presentador.

        Args:
            ui (Ui_MainWindow): Interfaz de la ventana principal ya 
                inicializada.
            oscilloscope (GWInstekGDS1000AU): Instancia activa del 
                controlador del osciloscopio.
            file_manager (FileManager): Instancia encargada de gestionar 
                I/O del disco y HDF5.
            analyzer_class (Type[LightningImpulseAnalyzer]): Clase 
                abstracta usada para instanciar analizadores.
        """
        super().__init__()
        self.ui = ui
        self.osc = oscilloscope
        self.fm = file_manager
        self.AnalyzerClass = analyzer_class

        # Variables de estado del ensayo.
        self.ref_analyzer = None

        # Almacenar datos según el número de canal activo.
        self.pending_analyzers = {}  # {1: info_ch1, 2: info_ch2 }
        self.last_acquired_data = {} # {1: (buffer, wave, real_wave, dt), 2:...}

        self.wave_count = 0
        self.ref_count = 0

        self.project_created = False # Bandera de creación de carpeta.

        # Hilos.
        self.wait_thread = None

        self._setup_ui()
        self._connect_signals()
        if self.osc.dso is not None:
            # Si el instrumento se conectó con éxito en main.py,
            # espera que la GUI esté visible.
            # 100 milisegundos después sincroniza el instrumento con la GUI.
            QTimer.singleShot(100, self.synchronize_instrument)

    def _setup_ui(self) -> None:
        r"""Configura escalas, unidades, menús dinámicos y la 
        arquitectura dual del gráfico pyqtgraph.

        .. note::
            Instancia validadores de expresiones regulares 
            (``QRegularExpressionValidator``) que operan en tiempo real 
            sobre los campos de texto, garantizando la integridad de datos:
            - **Solo positivos**: Para las condiciones ambientales y 
              atenuaciones (ej. Humedad, Temperatura).
            - **Positivos y Negativos**: Para los parámetros configurables 
              del hardware (Offset, Delay y Nivel de Trigger).
        """
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

        # Configuración inicial del gráfico (pyqtgraph).
        self.ui.graph_view.setBackground('w') # Fondo blanco.
        self.ui.graph_view.showGrid(x=True, y=True, alpha=0.3)

        # Variables para acumular ondas en memoria RAM.
        self.saved_waves_data = {}
        self.color_index = 0

        # Asignar Menú al botón creado en Qt Designer.
        self.visibility_menu = QMenu(self.ui.btn_visibility)
        self.ui.btn_visibility.setMenu(self.visibility_menu)

        # Acciones globales para el menú.
        self.action_show_all = QAction("Mostrar todas", self)
        self.action_show_all.triggered.connect(
            lambda: self._set_all_waves_visibility(True)
        )
        self.visibility_menu.addAction(self.action_show_all)

        self.action_hide_all = QAction("Ocultar todas", self)
        self.action_hide_all.triggered.connect(
            lambda: self._set_all_waves_visibility(False)
        )
        self.visibility_menu.addAction(self.action_hide_all)

        self.visibility_menu.addSeparator() # Agrega una línea separadora.

        # Definir el color y estilo para los textos.
        text_color = '#000000' # Negro
        label_style = {
            'color': text_color,
            'font-size': '12pt',
            'font-weight': 'bold'
        }

        # Crear la leyenda en la esquina superior derecha.
        self.legend = self.ui.graph_view.addLegend(
            offset=(10, 10),
            brush=pg.mkBrush(255, 255, 255, 255), # Fondo blanco.
            pen=pg.mkPen(color='k', width=1)      # Borde negro de 1px.
        )
        # Establecer el valor Z para que la leyenda esté por encima de las ondas.
        self.legend.setZValue(10)
        # Configurar la tipografía de la leyenda.
        self.legend.setLabelTextColor(text_color)
        self.legend.setLabelTextSize('11pt')

        # Color de los nombres de los ejes y el título.
        self.ui.graph_view.setLabel(
            'bottom',
            'Tiempo',
            units='s',
            **label_style
        )
        self.ui.graph_view.setLabel(
            'left',
            'Tensión',
            units='V',
            **label_style
        )
        self.ui.graph_view.setTitle(
            'Esperando captura...',
            color=text_color,
            size='14pt'
        )

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

        # Crear un ViewBox independiente para el Canal 2 (Corriente).
        self.view_box_ch2 = pg.ViewBox()
        self.ui.graph_view.scene().addItem(self.view_box_ch2)

        # Crear el eje derecho y vincularlo al nuevo ViewBox.
        self.right_axis = pg.AxisItem('right')
        self.right_axis.linkToView(self.view_box_ch2)
        self.ui.graph_view.getPlotItem().layout.addItem(self.right_axis, 2, 3)

        # Configurar el estilo y la etiqueta del eje derecho.
        self.right_axis.setLabel('Corriente', units='A', **label_style)
        self.right_axis.setPen(axis_pen)
        self.right_axis.setTextPen(axis_pen)
        self.right_axis.setZValue(-1)

        # Vincular el eje X del CH2 al eje X del gráfico del CH1.
        self.view_box_ch2.setXLink(self.ui.graph_view)

        def update_views():
            # Actualizar la geometría del ViewBox CH2 cuando cambie el CH1.
            self.view_box_ch2.setGeometry(
                self.ui.graph_view.getViewBox().sceneBoundingRect()
            )
            self.view_box_ch2.linkedViewChanged(
                self.ui.graph_view.getViewBox(), self.view_box_ch2.XAxis
            )

        # Conectar la señal de dimensionar ventana a la función de actualización.
        self.ui.graph_view.getViewBox().sigResized.connect(update_views)

        # Forzar una actualización inicial de las vistas.
        update_views()

    def _connect_signals(self) -> None:
        r"""Enlaza las señales emitidas por los widgets de la GUI con 
        los métodos internos del presentador."""
        # Botones principales.
        self.ui.btn_search_instrument.clicked.connect(
            self.search_manual_instrument
        )
        self.ui.btn_create_folder.clicked.connect(self.create_new_project)
        self.ui.btn_save_waveform.clicked.connect(self.save_waveform)
        self.ui.btn_export_results.clicked.connect(self.export_results)

        if DEBUG_MODE:
            self.ui.btn_wait_waveform.clicked.connect(self.load_tdg_waveform)
        else:
            self.ui.btn_wait_waveform.clicked.connect(self.receive_waveform)

        # Habilitadores.
        # Uso de lambda para descartar el argumento int de stateChanged.
        self.ui.attenuations_enabler.stateChanged.connect(
            lambda: self._toggle_attenuations()
        )

        # Handlers de Escala Vertical.
        self.ui.ch1_voltage_value.currentTextChanged.connect(
            lambda: self._update_v_scale(1)
        )
        self.ui.ch1_voltage_unit.currentTextChanged.connect(
            lambda u: self._change_voltage_unit(1, u)
        )

        self.ui.ch2_voltage_value.currentTextChanged.connect(
            lambda: self._update_v_scale(2)
        )
        self.ui.ch2_voltage_unit.currentTextChanged.connect(
            lambda u: self._change_voltage_unit(2, u)
        )

        # Handler de Escala Horizontal.
        self.ui.time_value.currentTextChanged.connect(
            lambda: self._update_t_scale()
        )
        self.ui.time_unit.currentTextChanged.connect(
            self._change_time_unit
        )

        # Handlers de Variables Continuas (Offset, Delay, Trigger Level).
        self.ui.ch1_offset_value.editingFinished.connect(
            lambda: self._update_offset(1)
        )
        self.ui.ch1_offset_unit.currentTextChanged.connect(
            lambda: self._update_offset(1)
        )

        self.ui.ch2_offset_value.editingFinished.connect(
            lambda: self._update_offset(2)
        )
        self.ui.ch2_offset_unit.currentTextChanged.connect(
            lambda: self._update_offset(2)
        )

        self.ui.delay_value.editingFinished.connect(
            self._update_delay
        )
        self.ui.delay_unit.currentTextChanged.connect(
            self._update_delay
        )

        self.ui.trigger_level_value.editingFinished.connect(
            self._update_trigger_level
        )
        self.ui.trigger_level_unit.currentTextChanged.connect(
            self._update_trigger_level
        )

        # Flanco de Trigger.
        self.ui.trigger_edge_positive.toggled.connect(
            lambda checked: self.osc.set_trigger_slope(0) if checked else None
        )
        self.ui.trigger_edge_negative.toggled.connect(
            lambda checked: self.osc.set_trigger_slope(1) if checked else None
        )

        # Actualización automática de Atenuaciones.
        CONFIG_CHANNELS = [
            ("ch1_resistive_divider_value", "Divisor resistivo (CH1)", 1),
            ("ch1_attenuator_value", "Atenuador (CH1)", 1),
            ("ch2_resistive_divider_value", "Divisor resistivo (CH2)", 2),
            ("ch2_attenuator_value", "Atenuador (CH2)", 2),
        ]

        for attr, label, ch_idx in CONFIG_CHANNELS:
            widget = getattr(self.ui, attr)
            widget.editingFinished.connect(
                lambda w=widget, l=label, c=ch_idx: (
                    self._on_attenuation_changed(w, l, c)
                )
            )

        # Handlers para los Radio Buttons del tipo de gráfico.
        self.ui.normalized_type_radio.toggled.connect(
            self._on_graph_type_changed
        )
        self.ui.real_type_radio.toggled.connect(
            self._on_graph_type_changed
        )

    def _update_results_gui(
            self, 
            analyzer: LightningImpulseAnalyzer
    ) -> None:
        r"""Actualiza el panel lateral de la GUI con los parámetros 
        calculados y realiza conversiones de escala.

        Extrae :math:`U_t`, :math:`T_1`, :math:`T_2` y el 
        :math:`\text{OS}` del diccionario de resultados.
        El valor de :math:`U_t` se divide por 1000 para renderizarse en 
        :math:`\unit{\kilo\volt}`, mientras que :math:`T_1` y :math:`T_2` 
        se multiplican por `1e6` para visualizarse en 
        :math:`\unit{\micro\second}`.

        Args:
            analyzer (LightningImpulseAnalyzer): Instancia con el 
                análisis matemático finalizado satisfactoriamente.
        """
        results = analyzer.results

        # Formatear o dejar en blanco los campos de resultados.
        def set_val(line_edit, key, scale=1.0):
            val = results.get(key)
            if val is not None:
                line_edit.setText(f"{val * scale:.2f}")
            else:
                line_edit.setText("") # En blanco si no se pudo calcular.

        set_val(self.ui.peak_voltage_value, "Ut", 1/1000.0)
        set_val(self.ui.t1_value, "T1", 1e6)
        set_val(self.ui.t2_value, "T2", 1e6)
        set_val(self.ui.os_value, "OS", 1.0)

    def _on_graph_type_changed(self) -> None:
        r"""Maneja el evento de cambio entre vista de curva real 
        (unidades del SI) y normalizada (p.u.)."""
        self._update_plot()

    def _update_plot(self) -> None:
        r"""Renderiza dinámicamente las ondas en el lienzo principal y 
        eje secundario (CH2).

        Limpia las vistas previas e itera sobre los buffers en memoria 
        para dibujar las trazas, asignando un feedback visual de colores 
        específico según el estado del análisis:
            - **Azul**: Tensión del Canal 1 analizada exitosamente.
            - **Verde**: Corriente del Canal 2 analizada exitosamente.
            - **Rojo**: Onda con análisis fallido (marca la leyenda 
              como "Error (CHX)").
        """
        # Título del gráfico basado en el número de ítem.
        item_number = self.ui.item_number_value.text().strip()
        item_year = self.ui.item_year_value.text().strip()
        graph_title = f"{item_number}-{item_year}"

        # Limpia el lienzo en cada actualización.
        self.ui.graph_view.clear() 
        self.view_box_ch2.clear()  
        self.legend.clear()   

        text_color = '#000000'
        label_style = {
            'color': text_color,
            'font-size': '12pt',
            'font-weight': 'bold'
        }

        # Bandera para seleccionar datos según el Radio Button activo.
        is_normalized = self.ui.normalized_type_radio.isChecked()

        # Graficar ondas guardadas visibles.
        for name, wave in self.saved_waves_data.items():
            if not wave["is_visible"]:
                continue

            color = wave["color"]
            t = wave["t"]

            if is_normalized:
                y_ch1 = wave["ch1_norm"]
                y_ch2 = wave.get("ch2_norm")
            else:
                y_ch1 = wave["ch1_real"]
                y_ch2 = wave.get("ch2_real")

            # Canal 1 (Línea continua - Eje Izquierdo)
            pen_ch1 = pg.mkPen(color=color, width=2)
            self.ui.graph_view.plot(
                t, y_ch1, name=f"{name} (CH1)", pen=pen_ch1
            )

            # Canal 2 (Línea punteada - Eje Derecho)
            if y_ch2 is not None:
                pen_ch2 = pg.mkPen(
                    color=color, width=2, style=Qt.DashLine
                )

                # Crear curva, añadir al Eje Derecho y en la leyenda.
                curve_ch2 = pg.PlotCurveItem(t, y_ch2, pen=pen_ch2)
                self.view_box_ch2.addItem(curve_ch2)
                self.legend.addItem(curve_ch2, f"{name} (CH2)")

        # Graficar las ondas actuales en el buffer (CH1 y/o CH2).
        has_pending = False
        for ch, info in self.pending_analyzers.items():
            has_pending = True
            analyzer = info["analyzer"]
            is_successful = info["success"]

            # Seleccionar el eje de tiempo adecuado (usa el alineado si existe).
            if analyzer.aligned_time_axis is not None:
                t_axis = analyzer.aligned_time_axis
            else:
                t_axis = analyzer.time_axis

            if is_successful:
                if is_normalized:
                    y_data = analyzer.test_voltage_curve_norm
                else:
                    y_data = analyzer.test_voltage_curve
                if ch == 1:
                    pen_color = (0, 100, 200) # Azul para CH1.
                    legend_name = "Actual (CH1)"
                else:
                    pen_color = (0, 150, 0) # Verde oscuro para CH2.
                    legend_name = "Actual (CH2)"
            else:
                y_data = analyzer.raw_voltage
                pen_color = (200, 0, 0) # Rojo para error.
                legend_name = f"Error (CH{ch})"

            # Dibujar la curva en el lienzo, más gruesa para destacar.
            if t_axis is not None and y_data is not None:
                pen = pg.mkPen(color=pen_color, width=3)
                
                if ch == 1:
                    # CH1 al eje izquierdo normal.
                    self.ui.graph_view.plot(
                        t_axis, y_data, name=legend_name, pen=pen
                    )
                else:
                    # CH2 al eje derecho.
                    curve_ch2_pending = pg.PlotCurveItem(
                        t_axis, y_data, pen=pen
                    )
                    self.view_box_ch2.addItem(curve_ch2_pending)
                    self.legend.addItem(curve_ch2_pending, legend_name)

        if has_pending:
            self.ui.graph_view.setTitle(
                "Onda(s) sin guardar",
                color=text_color,
                size='14pt',
                bold=True
            )
        else:
            self.ui.graph_view.setTitle(
                graph_title,
                color=text_color,
                size='14pt',
                bold=True
            )

        # Actualizar etiquetas de ejes.
        if is_normalized:
            self.ui.graph_view.setLabel(
                'left',
                'Tensión Normalizada',
                units='p.u.',
                **label_style
            )
            self.right_axis.setLabel(
                'Corriente Normalizada',
                units='p.u.',
                **label_style
            )
        else:
            self.ui.graph_view.setLabel(
                'left',
                'Tensión',
                units='V',
                **label_style
            )
            self.right_axis.setLabel(
                'Corriente',
                units='A',
                **label_style
            )

    def load_tdg_waveform(self) -> None:
        r"""Carga una onda sintética plana (TDG) desde el disco para 
        depuración de algoritmos (DEBUG_MODE) y estimación de la 
        incertidumbre del algoritmo según la norma IEC 61083-2.

        Abre un diálogo de selección de archivo nativo. Si ocurre un 
        fallo en la lectura, la excepción es capturada y notificada 
        mediante un ``QMessageBox`` interactivo.
        """
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
            # Leer el archivo usando la función de file_manager.py.
            metadata, data_list = self.fm.read_TDG_file(file_path)
            # Extraer dt y convertir la lista de tensión a un array de NumPy.
            dt = metadata['sampling_period']
            waveform = np.array(data_list)
            # inBuffer ficticio para que no falle el botón de Guardar.
            inBuffer = waveform

            # Simula leer en el canal principal activo.
            active_channel = 2 if self.ui.ch2_enabler.isChecked() else 1
            real_waveform = self._apply_hardware_attenuations(waveform, 
                active_channel
            )

            self.last_acquired_data = {}
            self.last_acquired_data[active_channel] = (inBuffer, 
                waveform, 
                real_waveform, 
                dt
            )

            self._process_and_plot_acquired_data()

        except Exception as e:
            QMessageBox.critical(
                None,
                "Error de Lectura",
                f"No se pudo cargar el archivo:\n{str(e)}"
            )

    # --- Funciones Lógicas ---

    def search_manual_instrument(self) -> None:
        r"""Fuerza un escaneo de puertos en el bus VISA para inicializar 
        o recuperar un osciloscopio compatible.

        Si se detecta un hardware fallido o desconectado, cierra la 
        sesión actual, recrea el `ResourceManager` y avisa al operador 
        de manera interactiva.
        """
        import pyvisa
        # Comprobar si el objeto existe y está activo.
        if self.osc.dso is not None:
            try:
                self.osc.dso.query('*IDN?')
                QMessageBox.information(
                    None,
                    "Aviso",
                    "El instrumento ya se encuentra conectado y "
                    "funcionando correctamente.",
                )
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
            QMessageBox.critical(
                None,
                "Error del Sistema",
                f"No se pudieron escanear los puertos:\n{e}"
            )
            return

        # Conectar al primer equipo que encuentre.
        if found_instruments:
            port = found_instruments[0]
            self.osc.connect(port)
            # Verificar el estado de la conexión.
            if self.osc.dso is not None:
                self.synchronize_instrument()
                QMessageBox.information(
                    None,
                    "Conexión Exitosa",
                    "Instrumento enlazado correctamente en el puerto:\n"
                    f"{port}"
                )
            else:
                QMessageBox.warning(
                    None,
                    "Error de Comunicación",
                    f"Se detectó un dispositivo en {port}, "
                    "pero rechazó la conexión."
                )
        else:
            QMessageBox.warning(
                None,
                "Instrumento no encontrado",
                "No se detectó hardware conectado a la PC.\n"
                "Revise el cable USB y asegúrese de que "
                "el osciloscopio esté encendido."
            )

    def _clear_dynamic_wave_menu(self) -> None:
        """Limpia las acciones dinámicas del menú de visibilidad."""
        static_actions = {self.action_show_all, self.action_hide_all}

        # list() evita saltos de índice al remover elementos
        for action in list(self.visibility_menu.actions()):
            if action not in static_actions and not action.isSeparator():
                self.visibility_menu.removeAction(action)

    def create_new_project(self) -> None:
        r"""Inicializa un ensayo nuevo o reanuda uno existente.

        Inyecta la memoria histórica a la GUI y aplica una capa de 
        seguridad (filtrado de strings) aplicando expresiones 
        regulares (``re.sub``) sobre los campos numéricos y de cliente 
        ingresados por el usuario. Esto elimina caracteres prohibidos 
        por el Sistema Operativo (``\\/*?:"<>|``) garantizando que la 
        creación física de las carpetas nunca colapse.
        """
        # Extraer y limpiar textos de la UI.
        item_number = self.ui.item_number_value.text().strip()
        item_year = self.ui.item_year_value.text().strip()
        client = self.ui.client_value.text().strip()

        # Validar que ningún campo esté vacío.
        if not item_number or not item_year:
            QMessageBox.warning(
                None,
                "Datos faltantes",
                "Complete el campo 'Item' para buscar o crear la carpeta."
            )
            return

        # Verificar los textos para evitar caracteres inválidos.
        pattern = r'[\\/*?:"<>|]'
        item_number = re.sub(pattern, "", item_number)
        item_year = re.sub(pattern, "", item_year)
        client = re.sub(pattern, "", client)

        folder_name = f"{item_number}-{item_year}"
        if client:
            folder_name += f" - {client}"

        # Abrir explorador de carpetas.
        base_dir = QFileDialog.getExistingDirectory(
            None, "Seleccionar ubicación para el ensayo", "", 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        # Si el usuario cierra la ventana o presiona cancelar,
        # aborta la operación.
        if not base_dir:
            return

        # Validación de carpeta existente.
        full_path = os.path.join(base_dir, folder_name)
        h5_path = os.path.join(
            full_path,
            "02 Analisis de datos",
            f"{item_number}-{item_year}.h5"
        )

        if os.path.exists(full_path):
            respuesta = QMessageBox.question(
                None,
                "Ensayo Existente",
                f"La carpeta '{folder_name}' ya existe.\n"
                "¿Desea abrir este ensayo y cargar las mediciones previas?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.No:
                return

            # Reanudar ensayo.
            self.fm.create_new_structure(folder_name, base_dir=base_dir)
            counts = self.fm.get_existing_wave_count(h5_path)
            self.wave_count, self.ref_count = counts
            self.ref_analyzer = None

            # Leer datos del HDF5.
            global_attrs, loaded_waves = self.fm.read_hdf5_waveforms(h5_path)

            # Autocompletar la UI.
            if global_attrs.get("Client"):
                self.ui.client_value.setText(str(global_attrs["Client"]))

            ui_mapping = {
                "Divider_CH1": self.ui.ch1_resistive_divider_value,
                "Attenuator_CH1": self.ui.ch1_attenuator_value,
                "Divider_CH2": self.ui.ch2_resistive_divider_value,
                "Attenuator_CH2": self.ui.ch2_attenuator_value,
            }

            for key, widget in ui_mapping.items():
                if key in global_attrs:
                    widget.setText(str(global_attrs[key]))

            # Restaurar Ondas en el Gráfico y Menú.
            self.saved_waves_data = {}
            self.color_index = 0

            # Limpiar acciones dinámicas previas del menú,
            # excepto Mostrar/Ocultar Todas.
            self._clear_dynamic_wave_menu()

            for h5_name, data in loaded_waves.items():
                # Separa el nombre en partes. 
                # Ej: "Onda_05_20260324" -> parts = ["Onda", "05", "20260324"].
                parts = h5_name.split("_")

                # Tomar el nombre "Onda" o "Referencia" y los 2 dígitos.
                # Onda_05_20260324 -> Onda_05.
                # Referencia_06_20260324 -> Referencia_06.
                if len(parts) >= 2:
                    display_name = f"{parts[0]}_{parts[1]}"
                else:
                    display_name = h5_name

                color = pg.intColor(self.color_index, hues=15, maxValue=200)
                self.color_index += 1

                self.saved_waves_data[display_name] = {
                    "t": data["t"],
                    "ch1_real": data["ch1_real"],
                    "ch1_norm": data["ch1_norm"],
                    "ch2_real": data["ch2_real"],
                    "ch2_norm": data["ch2_norm"],
                    "color": color,
                    "is_visible": True
                }

                # Agregar ondas al menú.
                action = QAction(display_name, self)
                action.setCheckable(True)
                action.setChecked(True)
                action.toggled.connect(
                    lambda checked, n=display_name: (
                        self._toggle_wave_visibility(n, checked)
                    )
                )
                self.visibility_menu.addAction(action)

            total_waves = self.wave_count + self.ref_count
            self.project_created = True
            self.ui.graph_name.setText(
                f"Reanudado. Ondas previas: {total_waves}"
            )
            self._update_plot()

            QMessageBox.information(
                None,
                "Ensayo Reanudado",
                f"Se han cargado {total_waves} onda(s) "
                "de la sesión anterior.\n\n"
                "IMPORTANTE:\n"
                "1. Actualizar 'Condiciones ambientales'.\n"
                "2. Capturar una nueva onda de referencia "
                "a tensión reducida."
            )
            return

        # Nuevo ensayo.
        self.fm.create_new_structure(folder_name, base_dir=base_dir)
        self.ref_analyzer = None
        self.wave_count = 0
        self.ref_count = 0
        self.ui.graph_name.setText("Ensayo inicializado")
        self.project_created = True

        # Limpiar ondas de la memoria RAM 
        # si abre otro proyecto en la misma sesión.
        self.saved_waves_data = {}
        self._clear_dynamic_wave_menu()
        self._update_plot()

        full_path_display = os.path.normpath(full_path)
        QMessageBox.information(
            None,
            "Éxito",
            f"Carpeta creada correctamente en:\n\n{full_path_display}"
        )

    def receive_waveform(self) -> None:
        r"""Instancia o cancela el hilo `WaitWaveformThread` para la 
        captura asíncrona de un disparo de hardware.

        Actúa como comportamiento "Toggle" sobre el botón de inicio de 
        captura en la interfaz.
        """
        if not self.osc.dso:
            QMessageBox.warning(
                None,
                "Error",
                "El osciloscopio no está conectado."
            )
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
        self.wait_thread.finished.connect(
            lambda: self.ui.btn_wait_waveform.setText("Iniciar")
        )
        self.wait_thread.start()

    @Slot()
    def process_waveform(self) -> None:
        r"""Slot ejecutado tras la detección exitosa de un disparo 
        emitido desde el hardware. 

        Descarga la memoria cruda de los canales habilitados, aplica 
        atenuadores y delega el análisis. Si no se encuentra ningún 
        canal activo pre-seleccionado, despliega un aviso interrumpiendo 
        la lógica.
        """
        self.ui.btn_wait_waveform.setEnabled(True)
        self.ui.btn_wait_waveform.setText("Iniciar")

        # Determinar los canales activos.
        ch1_active = self.ui.ch1_enabler.isChecked()
        ch2_active = self.ui.ch2_enabler.isChecked()

        if not ch1_active and not ch2_active:
            QMessageBox.warning(
                None,
                "Cuidado",
                "Se detectó disparo, pero no hay canales habilitados para leer."
            )
            return

        self.last_acquired_data = {}

        # Capturar ambos canales si están activos.
        if ch1_active:
            inBuffer, waveform, dt = self.osc.get_block_data(1)
            # Invertir atenuaciones del sistema 
            # para determinar el valor real de la onda.
            # Guardar temporalmente 
            # hasta que el usuario accione el botón "Guardar".
            if waveform is not None:
                real_waveform = self._apply_hardware_attenuations(waveform, 1)
                self.last_acquired_data[1] = (
                    inBuffer, waveform, real_waveform, dt
                )
        if ch2_active:
            inBuffer, waveform, dt = self.osc.get_block_data(2)
            if waveform is not None:
                real_waveform = self._apply_hardware_attenuations(waveform, 2)
                self.last_acquired_data[2] = (
                    inBuffer, waveform, real_waveform, dt
                )

        self._process_and_plot_acquired_data()

    def _process_and_plot_acquired_data(self) -> None:
        r"""Inyecta los arrays descargados a los analizadores 
        matemáticos y actualiza el estado gráfico.

        Ejecuta el modelo matemático en un entorno protegido. Si ocurre 
        una excepción (ej. ruido excesivo o corte prematuro), la captura 
        mediante ``try/except``, arroja un ``QMessageBox`` descriptivo y 
        almacena una bandera (``success = False``) que instruirá al 
        método de ploteo para dibujar la onda defectuosa en color rojo.
        """
        self.pending_analyzers = {}

        ch1_active = 1 in self.last_acquired_data
        ch2_active = 2 in self.last_acquired_data

        if ch1_active:
            _, _, real_waveform, dt = self.last_acquired_data[1]
            temp_analyzer = self.AnalyzerClass(real_waveform, dt, 
                                               sigma_fit=1.0)
            try:
                if self.ref_analyzer is None:
                    temp_analyzer.ref_lightning_impulse()
                else:
                    temp_analyzer.lightning_impulse(self.ref_analyzer)

                # Procesó la onda exitosamente.
                # Guardar el analizador exitoso y actualiza la GUI.
                self._update_results_gui(temp_analyzer)
                self.pending_analyzers[1] = {"analyzer": temp_analyzer, 
                                             "success": True}

            except ValueError as e:
                # Ocurrió algún problema al procesar la onda.
                # Capturar errores de análisis (Onda corta, ruido, etc.).
                # Actualiza los valores parciales calculados.
                # Indica que falló la matemática.
                self._update_results_gui(temp_analyzer)
                self.pending_analyzers[1] = {"analyzer": temp_analyzer, 
                                             "success": False}
                QMessageBox.warning(
                    None,
                    "Advertencia de Análisis CH1",
                    str(e)
                )

            except Exception as e:
                # Captura y muestra fallos críticos inesperados.
                self._update_results_gui(temp_analyzer)
                self.pending_analyzers[1] = {"analyzer": temp_analyzer, 
                                             "success": False}
                QMessageBox.critical(
                    None,
                    "Error Crítico de Análisis CH1",
                    "Ocurrió un error inesperado al "
                    "calcular los parámetros de la onda."
                )

        else:
            # Si CH1 no corrió, limpiamos el panel de resultados.
            self.ui.peak_voltage_value.setText("")
            self.ui.t1_value.setText("")
            self.ui.t2_value.setText("")
            self.ui.os_value.setText("")

        if ch2_active:
            _, _, real_waveform, dt = self.last_acquired_data[2]
            # CH2 solo es un contenedor adaptado para graficar.
            temp_analyzer2 = MockChannel2Analyzer(real_waveform, dt)
            self.pending_analyzers[2] = {"analyzer": temp_analyzer2, 
                                         "success": True}

        self._update_plot()

    def save_waveform(self) -> None:
        r"""Valida, empaqueta y persiste el evento de captura de onda, 
        actualizando el lienzo del historial.

        Guarda el objeto estructurado HDF5, exporta un CSV crudo como 
        backup y transfiere la traza exitosa al buffer 
        (``saved_waves_data``) añadiéndola al menú de visibilidad 
        gráfico. Requiere de la creación explícita de un proyecto previo 
        para ejecutarse.
        """
        # Validar que la carpeta existe antes de guardar la onda.
        if not self.project_created:
            QMessageBox.warning(
                None, 
                "Acción no permitida", 
                "Debe completar los Datos del ensayo y Crear la Carpeta\n "
                "para guardar los resultados."
            )
            return

        # Validar Condiciones Ambientales.
        t_db = self.ui.db_temperature_value.text().strip()
        t_wb = self.ui.wb_temperature_value.text().strip()
        rh = self.ui.relative_humidity_value.text().strip()
        ah = self.ui.absolute_humidity_value.text().strip()
        press = self.ui.pressure_value.text().strip()

        # all() verifica que ninguna de las cadenas de texto esté vacía ("").
        if not all([t_db, t_wb, rh, ah, press]):
            QMessageBox.warning(
                None,
                "Condiciones Incompletas",
                "Complete las 'Condiciones ambientales' antes de guardar."
            )
            return

        # Validar que haya datos capturados para guardar.
        if not self.last_acquired_data:
            QMessageBox.warning(
                None,
                "Aviso",
                "No hay onda adquirida para guardar."
            )
            return

        # Generar nombres para la UI y la base de datos.
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.ref_analyzer is None:
            self.ref_count += 1
            display_name = f"Referencia_{self.ref_count:02d}"
            wave_filename = f"Referencia_{self.ref_count:02d}_{timestamp_str}"
        else:
            self.wave_count += 1
            display_name = f"Onda_{self.wave_count:02d}"
            wave_filename = f"Onda_{self.wave_count:02d}_{timestamp_str}"

        item_number = self.ui.item_number_value.text().strip()
        item_year = self.ui.item_year_value.text().strip()
        item_full = f"{item_number}-{item_year}"

        # Empaquetar Datos Globales.
        global_data = {
            "Item": item_full,
            "Client": self.ui.client_value.text().strip(),
            "Divider_CH1": float(
                self.ui.ch1_resistive_divider_value.text() or 1.0
            ),
            "Attenuator_CH1": float(
                self.ui.ch1_attenuator_value.text() or 1.0
            ),
            "Divider_CH2": float(
                self.ui.ch2_resistive_divider_value.text() or 1.0
            ),
            "Attenuator_CH2": float(
                self.ui.ch2_attenuator_value.text() or 1.0
            )
        }

        # Extraer analizador.
        analyzer_ch1 = self.pending_analyzers.get(1, {}).get("analyzer")
        success_ch1 = self.pending_analyzers.get(1, {}).get("success", False)
        res = analyzer_ch1.results if analyzer_ch1 else {}

        # Empaquetar Atributos de Onda.
        wave_data = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "T_DB": float(t_db),
            "T_WB": float(t_wb),
            "RH": float(rh),
            "AH": float(ah),
            "Pressure": float(press),
            "Polarity": analyzer_ch1.polarity if analyzer_ch1 else "N/A",
            "Peak_Voltage": res.get("Ut"),
            "T1": res.get("T1"),
            "T2": res.get("T2"),
            "Overshoot": res.get("OS")
        }

        # Empaquetar Datos de Tiempo.
        time_data = {
            "raw": analyzer_ch1.time_axis if analyzer_ch1 else None,
            "aligned": analyzer_ch1.aligned_time_axis if analyzer_ch1 else None
        }

        # Empaquetar Datos de CH1.
        ch1_data = {
            "raw": analyzer_ch1.raw_voltage if analyzer_ch1 else None,
            "test": analyzer_ch1.test_voltage_curve if analyzer_ch1 else None,
            "norm": analyzer_ch1.test_voltage_curve_norm if analyzer_ch1 else None
        }

        # Empaquetar Datos de CH2 (Opcional).
        ch2_data = None
        if 2 in self.pending_analyzers:
            analyzer_ch2 = self.pending_analyzers[2]["analyzer"]
            ch2_data = {
                "raw": analyzer_ch2.raw_voltage,
                "test": analyzer_ch2.test_voltage_curve,
                "norm": analyzer_ch2.test_voltage_curve_norm
            }

        # Guardar HDF5.
        h5_file_path = self.fm.analysis / f"{item_full}.h5"

        self.fm.append_to_hdf5(
            file_path = h5_file_path, 
            wave_name = wave_filename, 
            global_data = global_data, 
            wave_data = wave_data, 
            time_data = time_data,
            ch1_data = ch1_data, 
            ch2_data = ch2_data
        )

        # Guardar respaldo original de la onda.
        if 1 in self.last_acquired_data:
            waveform1 = self.last_acquired_data[1][1]
            path1 = self.fm.get_new_filename(filename=f"{wave_filename}_V", 
                                             extension=".csv")
            self.fm.create_csv(waveform1, path1)

        if 2 in self.last_acquired_data:
            waveform2 = self.last_acquired_data[2][1]
            path2 = self.fm.get_new_filename(filename=f"{wave_filename}_A", 
                                             extension=".csv")
            self.fm.create_csv(waveform2, path2)

        # Actualizar UI, Menú y Gráficos.
        if success_ch1:
            if self.ref_analyzer is None:
                self.ref_analyzer = analyzer_ch1

            color = pg.intColor(self.color_index, hues=15, maxValue=200)
            self.color_index += 1

            if analyzer_ch1.aligned_time_axis is not None:
                t_data_plot = analyzer_ch1.aligned_time_axis
            else:
                t_data_plot = analyzer_ch1.time_axis

            # Leer datos de CH2 para graficarlo si está activo.
            ch2_real_plot = None
            ch2_norm_plot = None
            if 2 in self.pending_analyzers:
                analyzer_ch2 = self.pending_analyzers[2]["analyzer"]
                ch2_real_plot = analyzer_ch2.test_voltage_curve
                ch2_norm_plot = analyzer_ch2.test_voltage_curve_norm

            self.saved_waves_data[display_name] = {
                "t": t_data_plot,
                "ch1_real": analyzer_ch1.test_voltage_curve,
                "ch1_norm": analyzer_ch1.test_voltage_curve_norm,
                "ch2_real": ch2_real_plot,
                "ch2_norm": ch2_norm_plot,
                "color": color,
                "is_visible": True
            }

            action = QAction(display_name, self)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(
                lambda checked, n=display_name: (
                    self._toggle_wave_visibility(n, checked)
                )
            )
            self.visibility_menu.addAction(action)

        self.ui.graph_name.setText(display_name)
        QMessageBox.information(
            None,
            "Guardado",
            f"La {display_name} fue guardada exitosamente."
        )

        # Avanzar el contador general y limpiar registros temporales.
        self.last_acquired_data = {}
        self.pending_analyzers = {}
        self._update_plot()

    def _apply_hardware_attenuations(
            self, 
            waveform: np.ndarray, 
            channel: int
    ) -> np.ndarray:
        r"""Aplica la constante escalar nominal real de atenuación sobre 
        la traza discreta.

        Args:
            waveform (np.ndarray): Array crudo discreto de la señal en 
                :math:`\unit{\volt}`.
            channel (int): Canal a atenuar (1 o 2).

        Returns:
            np.ndarray: Vector de datos post-escalado con los divisores 
                ingresados en la interfaz gráfica.
        """
        if channel == 1:
            divider = float(self.ui.ch1_resistive_divider_value.text())
            attenuator = float(self.ui.ch1_attenuator_value.text())
        else:
            divider = float(self.ui.ch2_resistive_divider_value.text())
            attenuator = float(self.ui.ch2_attenuator_value.text())

        return waveform * divider * attenuator

    def _check_attenuation_value(
            self, 
            line_edit: QLineEdit, 
            field_name: str
    ) -> None:
        r"""Valida que la entrada del usuario en atenuadores sea un 
        número flotante estrictamente mayor a 0.

        .. note::
            Actúa como un **fallback (mitigación de errores)**. Si el 
            usuario borra por accidente el valor del divisor, lo deja en 
            blanco, ingresa un cero, o ingresa caracteres inválidos, el 
            presentador captura el fallo, advierte al operador y 
            restaura el valor por defecto (``"1.0"``) automáticamente.

        Args:
            line_edit (QLineEdit): Referencia al widget de entrada de 
                texto modificado en la vista.
            field_name (str): Etiqueta descriptiva del campo de texto a 
                usar en caso de advertencias gráficas.
        """
        text = line_edit.text().strip()
        # Si el campo está vacío, se asigna por defecto: 1.0.
        if not text:
            line_edit.setText("1.0")
            return
        try:
            val = float(text)
            if val <= 0:
                QMessageBox.warning(
                    None,
                    "Valor Inválido",
                    f"El valor en '{field_name}' debe ser mayor a 0.\n"
                    "Se restaurará a 1.0."
                )
                line_edit.setText("1.0")
        except ValueError:
            QMessageBox.warning(
                None,
                "Valor Inválido",
                f"El valor en '{field_name}' no es reconocido.\n"
                "Se restaurará a 1.0."
            )
            line_edit.setText("1.0")

    def _on_attenuation_changed(
            self, 
            line_edit: QLineEdit, 
            field_name: str, 
            channel: int
    ) -> None:
        r"""Fuerza un reprocesamiento del buffer temporal si el usuario 
        ajusta un atenuador post-captura.

        Args:
            line_edit (QLineEdit): Puntero al widget de origen del cambio.
            field_name (str): Descripción utilizada en la verificación 
                del atenuador interno.
            channel (int): Canal a reprocesar (1 o 2).
        """
        # Valida que el texto ingresado sea correcto.
        self._check_attenuation_value(line_edit, field_name)

        # Si hay una onda guardada en la memoria temporal,
        # la reprocesa inmediatamente.
        if channel in self.last_acquired_data:
            inBuffer, waveform, _, dt = self.last_acquired_data[channel]
            real_waveform = self._apply_hardware_attenuations(
                waveform, channel
            )
            self.last_acquired_data[channel] = (
                inBuffer, waveform, real_waveform, dt
            )

            # Reprocesa y grafica con el nuevo factor.
            self._process_and_plot_acquired_data()

    def _toggle_attenuations(self) -> None:
        r"""Conmuta dinámicamente el estado habilitado/deshabilitado de 
        los atenuadores de hardware en la GUI."""
        state = self.ui.attenuations_enabler.isChecked()
        self.ui.ch1_resistive_divider_value.setEnabled(state)
        self.ui.ch1_attenuator_value.setEnabled(state)
        self.ui.ch2_resistive_divider_value.setEnabled(state)
        self.ui.ch2_attenuator_value.setEnabled(state)

    def _update_v_scale(self, channel: int) -> None:
        r"""Sincroniza y envía el valor de escala vertical (V/div) hacia 
        el osciloscopio vía SCPI.

        Extrae el estado actual de los selectores visuales dinámicamente 
        sin requerir el paso de parámetros desde el emisor de la señal.

        Args:
            channel (int): Canal a configurar (1 o 2).
        """
        if channel == 1:
            val_str = self.ui.ch1_voltage_value.currentText()
            unit_str = self.ui.ch1_voltage_unit.currentText()
        elif channel == 2:
            val_str = self.ui.ch2_voltage_value.currentText()
            unit_str = self.ui.ch2_voltage_unit.currentText()
        else:
            return

        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_channel_scale(channel, scale)

    def _update_t_scale(self) -> None:
        r"""Sincroniza y envía el valor de escala horizontal (s/div) 
        hacia el osciloscopio vía SCPI."""
        val_str = self.ui.time_value.currentText()
        unit_str = self.ui.time_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_timebase_scale(scale)

    def _update_offset(self, channel: int) -> None:
        r"""Sincroniza y actualiza la inyección de offset vertical de un 
        canal en el instrumento.

        Args:
            channel (int): Canal a configurar (1 o 2).
        """
        if channel == 1:
            val_str = self.ui.ch1_offset_value.text()
            unit_str = self.ui.ch1_offset_unit.currentText()
        else:
            val_str = self.ui.ch2_offset_value.text()
            unit_str = self.ui.ch2_offset_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_channel_offset(channel, scale)

    def _update_delay(self) -> None:
        r"""Actualiza la posición del retardo horizontal (delay) del 
        barrido temporal."""
        val_str = self.ui.delay_value.text()
        unit_str = self.ui.delay_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_timebase_position(scale)

    def _update_trigger_level(self) -> None:
        r"""Configura el umbral de tensión absoluto para activar el 
        circuito de disparo."""
        val_str = self.ui.trigger_level_value.text()
        unit_str = self.ui.trigger_level_unit.currentText()
        scale = self.osc.process_multipliers(val_str, unit_str)
        if scale is not None:
            self.osc.set_trigger_level(scale)

    @Slot(str)
    def _handle_thread_error(self, error_msg: str) -> None:
        r"""Maneja e informa fallas críticas surgidas en el sub-hilo de 
        adquisición asíncrona.

        Args:
            error_msg (str): Detalle del volcado de la excepción 
                proveniente del hilo de sondeo.
        """
        self.ui.btn_wait_waveform.setText("Iniciar")
        QMessageBox.critical(
            None,
            "Error de Comunicación",
            f"Se produjo un error:\n{error_msg}"
        )

    def synchronize_instrument(self) -> None:
        r"""Restablece la configuración de fábrica del instrumento, 
        programando la re-sincronización de la GUI en diferido."""
        if not self.osc.dso:
            return
        # Restablecer instrumento a valores de fábrica.
        self.osc.default_settings()
        # Espera 1500 ms para que procese el reinicio interno.
        QTimer.singleShot(1500, self._continue_synchronization)

    def _continue_synchronization(self) -> None:
        r"""Aplica masivamente el estado actual de los selectores de la 
        GUI hacia la memoria del instrumento."""
        if not self.osc.dso:
            return

        # Escala Vertical y Offset.
        self._update_v_scale(1)
        self._update_offset(1)
        self._update_v_scale(2)
        self._update_offset(2)

        # Escala Horizontal y Delay.
        self._update_t_scale()
        self._update_delay()

        # Trigger.
        self._update_trigger_level()
        slope = 0 if self.ui.trigger_edge_positive.isChecked() else 1
        self.osc.set_trigger_slope(slope)

        # Habilitar/Deshabilitar canales según el estado inicial de la GUI.
        self.osc.set_channel_display(
            1, 1 if self.ui.ch1_enabler.isChecked() else 0
        )
        self.osc.set_channel_display(
            2, 1 if self.ui.ch2_enabler.isChecked() else 0
        )

    def _change_voltage_unit(self, channel: int, unit: str) -> None:
        r"""Modifica dinámicamente el Combobox de magnitudes de tensión 
        basándose en la unidad activa.

        Bloquea temporalmente el envío de señales Qt (`blockSignals`) 
        para prevenir fallos en la ejecución.

        .. note::
            **Uso de `blockSignals(True)`:** Al vaciar (`.clear()`) y 
            rellenar (`.addItems()`) el ComboBox con las nuevas opciones, 
            el widget emitiría automáticamente múltiples señales 
            `currentTextChanged`. Esto causaría una "condición de 
            carrera", enviando valores vacíos o erróneos al osciloscopio 
            y provocando fallos en la ejecución. El bloqueo silencia 
            estas emisiones temporales hasta que la interfaz esté 
            completamente actualizada y estabilizada.

        Args:
            channel (int): Canal a configurar (1 o 2).
            unit (str): Unidad seleccionada en GUI ("mV" o "V").
        """
        # Si la unidad no existe (ej. "kV"), aborta y no modifica nada.
        if unit not in self.voltage_values:
            return

        if channel == 1:
            value_selector = self.ui.ch1_voltage_value
        else:
            value_selector = self.ui.ch2_voltage_value

        current_value = value_selector.currentText()

        # Bloquear señales temporalmente mientras vacia y llena la lista.
        value_selector.blockSignals(True)
        try:
            value_selector.clear()
            valid_options = self.voltage_values[unit]
            value_selector.addItems(valid_options)

            # Mantiene el valor actual si es válido, 
            # sino fuerza el primer elemento de la nueva lista.
            if current_value in valid_options:
                value_selector.setCurrentText(current_value)
            else:
                value_selector.setCurrentText(valid_options[0])
        finally:
            value_selector.blockSignals(False)

        self._update_v_scale(channel)

    def _change_time_unit(self, unit: str) -> None:
        r"""Modifica dinámicamente el Combobox de la base de tiempo 
        horizontal basándose en la unidad.

        Bloquea temporalmente el envío de señales Qt (`blockSignals`) 
        para prevenir fallos en la ejecución.

        .. note::
            **Uso de `blockSignals(True)`:** Al vaciar (`.clear()`) y 
            rellenar (`.addItems()`) el ComboBox con las nuevas opciones, 
            el widget emitiría automáticamente múltiples señales 
            `currentTextChanged`. Esto causaría una "condición de 
            carrera", enviando valores vacíos o erróneos al osciloscopio 
            y provocando fallos en la ejecución. El bloqueo silencia 
            estas emisiones temporales hasta que la interfaz esté 
            completamente actualizada y estabilizada.

        Args:
            unit (str): Unidad seleccionada en GUI ("ns", "µs", "ms", "s").
        """
        # Si la unidad no existe (ej. "ps"), aborta y no modifica nada.
        if unit not in self.time_values:
            return

        value_selector = self.ui.time_value
        current_value = value_selector.currentText()

        # Bloquear señales temporalmente mientras vacia y llena la lista.
        value_selector.blockSignals(True)
        try:
            value_selector.clear()
            valid_options = self.time_values[unit]
            value_selector.addItems(valid_options)

            # Mantiene el valor actual si es válido, 
            # sino fuerza el primer elemento de la nueva lista.
            if current_value in valid_options:
                value_selector.setCurrentText(current_value)
            else:
                value_selector.setCurrentText(valid_options[0])
        finally:
            value_selector.blockSignals(False)

        self._update_t_scale()

    def _toggle_wave_visibility(self, name: str, checked: bool) -> None:
        r"""Conmuta y solicita el renderizado inmediato individual de 
        una curva almacenada.

        Args:
            name (str): Etiqueta clave bajo la cual la onda de sesión 
                fue guardada.
            checked (bool): Estado de visibilidad (True: visible, 
                False: oculta).
        """
        if name in self.saved_waves_data:
            self.saved_waves_data[name]["is_visible"] = checked
            # Refresca el gráfico manteniendo la onda actual si existe.
            self._update_plot()

    def _set_all_waves_visibility(self, visible: bool) -> None:
        r"""Aplica un estado de visibilidad a todo el historial de 
        curvas del gráfico.

        Args:
            visible (bool): Estado de visibilidad (True: todas expuestas, 
                False: todas ocultas).
        """
        # Actualizar el estado de visibilidad de las ondas.
        for name in self.saved_waves_data:
            self.saved_waves_data[name]["is_visible"] = visible
        # Sincronizar visualmente los tildes en el menú.
        for action in self.visibility_menu.actions():
            if action.isCheckable():
                # Bloquear señales temporalmente 
                # para que no redibuje por cada item.
                action.blockSignals(True)
                action.setChecked(visible)
                action.blockSignals(False)
        self._update_plot()

    def export_results(self) -> None:
        r"""Exporta una tabla de resultados analíticos recopilados hacia 
        ficheros estructurados (Excel/CSV).

        Si la persistencia en disco se efectúa exitosamente, llama a 
        rutinas del SO para invocar al explorador nativo. Si un fichero 
        está bloqueado o existe falta de permisos de escritura, la 
        excepción interna se procesa y se advierte en pantalla 
        gráficamente en lugar de romper el hilo.

        .. note::
            Utiliza módulos de bajo nivel (``platform`` y ``subprocess``) 
            para optimizar la experiencia de usuario, dándole acceso 
            inmediato a la tabla para su revisión, invocando al 
            explorador de archivos nativo del sistema operativo (Windows 
            ``explorer``, macOS ``open`` o Linux ``xdg-open``) y 
            apuntando al documento recién creado.
        """
        # Validar estado.
        if not self.project_created:
            QMessageBox.warning(
                None,
                "Acción no permitida",
                "Debe crear o abrir un ensayo primero antes de exportar."
            )
            return

        # Filtrado estricto de cadenas extraídas de la GUI.
        pattern = r'[\\/*?:"<>|]'
        item_number = re.sub(
            pattern, "", self.ui.item_number_value.text().strip()
        )
        item_year = re.sub(
            pattern, "", self.ui.item_year_value.text().strip()
        )
        client = re.sub(
            pattern, "", self.ui.client_value.text().strip()
        )

        # Validar que los campos esenciales no queden vacios.
        if not item_number or not item_year:
            QMessageBox.warning(
                None,
                "Datos faltantes",
                "Los campos de número y año no pueden quedar vacíos."
            )
            return

        item_full = f"{item_number}-{item_year}"
        h5_file_path = self.fm.analysis / f"{item_full}.h5"

        # Obtener DataFrame del FileManager.
        df = self.fm.export_hdf5_results_to_dataframe(h5_file_path)

        if df is None or df.empty:
            QMessageBox.information(
                None,
                "Sin datos",
                "No hay ondas de ensayo guardadas para exportar.\n"
                "Recuerde que las ondas de referencia no se exportan."
            )
            return

        # Estandarizar nombre del archivo.
        if client:
            default_name = f"{item_full} - {client} - Resultados"
        else:
            default_name = f"{item_full} - Resultados"

        # Direccionar por defecto a la carpeta "03 Resultados".
        default_path = str(self.fm.results / default_name)
        
        # Diálogo de guardado en formato XLSX y CSV.
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.ui.centralwidget,
            "Exportar Resultados",
            default_path,
            "Excel (*.xlsx);;Archivos CSV (*.csv)"
        )

        if not file_path:
            return # El usuario canceló el diálogo.

        # Garantizar que el archivo contenga la extensión obligatoria
        # Previene Fallos si el SO o el usuario no agregan la terminación.
        if "Excel" in selected_filter and not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        elif "CSV" in selected_filter and not file_path.lower().endswith('.csv'):
            file_path += '.csv'

        # Escribir el archivo.
        try:
            if file_path.lower().endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            else:
                # Usar la coma como separador de columnas 
                # y el punto para los decimales.
                df.to_csv(file_path, index=False, sep=',', decimal='.')

            # Abrir el explorador de archivos en el documento seleccionado.
            file_path_os = os.path.normpath(file_path)
            current_os = platform.system()

            if current_os == "Windows": # Windows.
                subprocess.run(['explorer', '/select,', file_path_os])
            elif current_os == "Darwin": # macOS.
                subprocess.run(['open', '-R', file_path_os])
            else: # Linux.
                subprocess.run(['xdg-open', os.path.dirname(file_path_os)])

        except Exception as e:
            msg = (
                f"Se produjo un error al intentar guardar el "
                f"archivo:\n{e}\n\n"
                "Asegúrese de que el archivo no esté abierto en otro programa."
            )
            QMessageBox.critical(None, "Error al exportar", msg)