"""Dual-cursor waveform analysis tool.

Provides a GUI to load a 2-column CSV or XLSX file, plot the waveform without interpolation,
and extract coordinates and deltas (ΔX, ΔY) using two selectable cursors.
"""

import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QFileDialog, QLabel, QMessageBox,
                               QRadioButton, QButtonGroup, QGroupBox)
from PySide6.QtCore import Qt

# Constantes de configuración de UI
WINDOW_TITLE = "Dual-Cursor Waveform Analyzer"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
DEFAULT_UI_FONT_SIZE = "14px"


class WaveformAnalyzer(QMainWindow):
    """Main application window for visualizing and analyzing waveforms.

    Attributes:
        x_data (np.ndarray | None): Array containing X-axis data.
        y_data (np.ndarray | None): Array containing Y-axis data.
        cursor1_idx (int | None): Array index of the data point selected by Cursor 1.
        cursor2_idx (int | None): Array index of the data point selected by Cursor 2.
    """

    def __init__(self):
        """Initializes the window, variables, and UI components."""
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.x_data = None
        self.y_data = None
        self.cursor1_idx = None
        self.cursor2_idx = None

        self._setup_ui()

    def _setup_ui(self):
        """Configures the main layout, control panel, and graph widget."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Panel lateral (Controles)
        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.btn_load = QPushButton("Load Data (CSV/XLSX)")
        self.btn_load.clicked.connect(self._load_data)
        self.lbl_status = QLabel("Status: Waiting for data...")

        # Selector de cursor activo
        self.cursor_group = QGroupBox("Active Cursor")
        cursor_layout = QVBoxLayout()
        self.radio_c1 = QRadioButton("Cursor 1 (Red)")
        self.radio_c2 = QRadioButton("Cursor 2 (Green)")
        self.radio_c1.setChecked(True)
        cursor_layout.addWidget(self.radio_c1)
        cursor_layout.addWidget(self.radio_c2)
        self.cursor_group.setLayout(cursor_layout)

        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.radio_c1, 1)
        self.btn_group.addButton(self.radio_c2, 2)

        # Etiquetas de estado y mediciones
        style = f"font-size: {DEFAULT_UI_FONT_SIZE}; font-weight: bold;"
        self.lbl_c1 = QLabel("Cursor 1:\nX: --\nY: --")
        self.lbl_c2 = QLabel("Cursor 2:\nX: --\nY: --")
        self.lbl_deltas = QLabel("ΔX: --\nΔY: --")
        
        self.lbl_c1.setStyleSheet(style + " color: red;")
        self.lbl_c2.setStyleSheet(style + " color: green;")
        self.lbl_deltas.setStyleSheet(style)

        control_panel.addWidget(self.btn_load)
        control_panel.addSpacing(10)
        control_panel.addWidget(self.lbl_status)
        control_panel.addSpacing(20)
        control_panel.addWidget(self.cursor_group)
        control_panel.addSpacing(20)
        control_panel.addWidget(self.lbl_c1)
        control_panel.addSpacing(10)
        control_panel.addWidget(self.lbl_c2)
        control_panel.addSpacing(20)
        control_panel.addWidget(self.lbl_deltas)

        # Panel principal (Gráfico)
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Gráfico tipo scatter plot
        self.plot_curve = self.plot_widget.plot(
            pen=None,
            symbol='o',
            symbolSize=5,
            symbolBrush='b'
        )

        # Líneas de referencia (Crosshairs)
        pen_c1 = pg.mkPen('r', style=Qt.PenStyle.DashLine, width=1.5)
        pen_c2 = pg.mkPen('g', style=Qt.PenStyle.DashLine, width=1.5)
        
        self.v_line1 = pg.InfiniteLine(angle=90, movable=False, pen=pen_c1)
        self.h_line1 = pg.InfiniteLine(angle=0, movable=False, pen=pen_c1)
        self.v_line2 = pg.InfiniteLine(angle=90, movable=False, pen=pen_c2)
        self.h_line2 = pg.InfiniteLine(angle=0, movable=False, pen=pen_c2)
        
        self.plot_widget.addItem(self.v_line1, ignoreBounds=True)
        self.plot_widget.addItem(self.h_line1, ignoreBounds=True)
        self.plot_widget.addItem(self.v_line2, ignoreBounds=True)
        self.plot_widget.addItem(self.h_line2, ignoreBounds=True)
        
        self.v_line1.hide()
        self.h_line1.hide()
        self.v_line2.hide()
        self.h_line2.hide()

        # Evento de clic
        self.plot_widget.scene().sigMouseClicked.connect(self._on_plot_clicked)

        # Ensamblaje de paneles
        layout.addLayout(control_panel, stretch=1)
        layout.addWidget(self.plot_widget, stretch=4)

    def _load_data(self):
        """Loads a 2-column data file (CSV, TXT, XLSX) into the internal arrays.
        
        Assumes the file contains no headers and uses the first two columns.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "", "Data Files (*.csv *.txt *.xlsx *.xls);;All Files (*)"
        )
        if not file_path:
            return

        try:
            # Ruteo según extensión del archivo
            if file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, header=None, usecols=[0, 1])
                data = df.to_numpy()
            else:
                data = np.loadtxt(file_path, delimiter=',')
            
            if data.ndim != 2 or data.shape[1] < 2:
                raise ValueError("Data must contain at least 2 columns (X and Y).")
            
            self.x_data = data[:, 0]
            self.y_data = data[:, 1]
            
            # Reset de estado lógico y visual
            self.cursor1_idx = None
            self.cursor2_idx = None
            self.v_line1.hide()
            self.h_line1.hide()
            self.v_line2.hide()
            self.h_line2.hide()
            self._update_labels()

            self.lbl_status.setText(f"Status: Data loaded ({len(self.x_data)} pts)")
            self.plot_curve.setData(self.x_data, self.y_data)
            self.plot_widget.autoRange()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{e}")

    def _on_plot_clicked(self, event):
        """Handles mouse clicks, calculates the nearest neighbor, and updates the active cursor.

        Args:
            event (pyqtgraph.GraphicsScene.mouseEvents.MouseClickEvent): Emitted click event.
        """
        if self.x_data is None or event.button() != Qt.MouseButton.LeftButton:
            return

        pos = event.scenePos()
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            x_val = mouse_point.x()

            # Búsqueda de índice del punto más cercano en el eje X
            idx = (np.abs(self.x_data - x_val)).argmin()
            active_cursor = self.btn_group.checkedId()
            
            if active_cursor == 1:
                self.cursor1_idx = idx
                self.v_line1.setPos(self.x_data[idx])
                self.h_line1.setPos(self.y_data[idx])
                self.v_line1.show()
                self.h_line1.show()
            else:
                self.cursor2_idx = idx
                self.v_line2.setPos(self.x_data[idx])
                self.h_line2.setPos(self.y_data[idx])
                self.v_line2.show()
                self.h_line2.show()

            self._update_labels()

    def _update_labels(self):
        """Calculates differences and updates coordinate strings in the UI labels."""
        c1_str = "X: --\nY: --"
        c2_str = "X: --\nY: --"
        dx_str = "--"
        dy_str = "--"

        if self.cursor1_idx is not None:
            x1, y1 = self.x_data[self.cursor1_idx], self.y_data[self.cursor1_idx]
            c1_str = f"X: {x1*1e6:.8f}\nY: {y1:.4f}"

        if self.cursor2_idx is not None:
            x2, y2 = self.x_data[self.cursor2_idx], self.y_data[self.cursor2_idx]
            c2_str = f"X: {x2*1e6:.8f}\nY: {y2:.4f}"

        # Cálculo de diferencias
        if self.cursor1_idx is not None and self.cursor2_idx is not None:
            dx = self.x_data[self.cursor2_idx] - self.x_data[self.cursor1_idx]
            dy = self.y_data[self.cursor2_idx] - self.y_data[self.cursor1_idx]
            dx_str = f"{dx*1e6:.8f}"
            dy_str = f"{dy:.4f}"

        self.lbl_c1.setText(f"Cursor 1:\n{c1_str}")
        self.lbl_c2.setText(f"Cursor 2:\n{c2_str}")
        self.lbl_deltas.setText(f"ΔX: {dx_str}\nΔY: {dy_str}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaveformAnalyzer()
    window.show()
    sys.exit(app.exec())