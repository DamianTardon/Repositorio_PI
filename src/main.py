import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import pyqtgraph as pg

# Liberías de este proyecto
from file_manager import FileManager
from impulse_analyzer import LightningImpulseAnalyzer
from gw_instek_gds1000a_u import GWInstekGDS1000AU
from controller import MainController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cargar la interfaz
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ruta_ui = os.path.join(current_directory, "graphic_user_interface.ui")
    ui_file = QFile(ruta_ui)
    ui_file.open(QFile.ReadOnly)
    loader = QUiLoader()
    loader.registerCustomWidget(pg.PlotWidget)
    window = loader.load(ui_file)
    ui_file.close()

    # Instanciar los componentes del backend.
    oscilloscope = GWInstekGDS1000AU()
    file_system = FileManager()

    # Iniciar el Controlador (Vista - Modelo).
    app_controller = MainController(window, oscilloscope, file_system, LightningImpulseAnalyzer)

    # Mostrar y ejecutar.
    window.show()
    sys.exit(app.exec())