import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_graphic_user_interface import Ui_MainWindow

# Liberías de este proyecto.
from file_manager import FileManager
from impulse_analyzer import LightningImpulseAnalyzer
from gw_instek_gds1000a_u import GWInstekGDS1000AU
from controller import MainController

class MainWindow(QMainWindow, Ui_MainWindow):
    # Unir la ventana de PySide6 con el diseño generado.
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Instanciar la ventana compilada.
    window = MainWindow()

    # Instanciar los componentes del backend.
    oscilloscope = GWInstekGDS1000AU()
    file_system = FileManager()

    # Iniciar el Controlador (Vista - Modelo).
    app_controller = MainController(window, oscilloscope, file_system, LightningImpulseAnalyzer)

    # Mostrar y ejecutar.
    window.show()
    sys.exit(app.exec())