"""Punto de entrada principal para el software de metrología de impulsos atmosféricos de alta tensión.

Orquesta la inicialización del sistema bajo el patrón de diseño arquitectónico 
Modelo-Vista-Presentador (MVP). Está diseñado para el análisis de ondas de impulso 
atmosféricos normalizados de :math:`\qty{1.2/50}{\micro\second}`.

Instancia los módulos físicos e inyecta las dependencias al presentador principal antes 
de ceder el control al bucle de eventos de Qt. Los componentes orquestados incluyen:
    * Hardware de adquisición (comunicación VISA).
    * Almacenamiento local (HDF5).
    * Motor de cálculo matemático y validación de impulsos.
    * Interfaz gráfica de usuario (GUI).
"""
from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_graphic_user_interface import Ui_MainWindow

# Liberías de este proyecto.
from file_manager import FileManager
from impulse_analyzer import LightningImpulseAnalyzer
from gw_instek_gds1000a_u import GWInstekGDS1000AU
from presenter import MainPresenter

class MainWindow(QMainWindow, Ui_MainWindow):
    """Vista principal de la aplicación construida con PySide6.

    Hereda de :class:`PySide6.QtWidgets.QMainWindow` y de la clase generada 
    automáticamente :class:`ui_graphic_user_interface.Ui_MainWindow` (compilada desde 
    un archivo ``.ui`` de Qt Designer). Actúa como la Vista en el patrón MVP.
    
    Su responsabilidad es estrictamente pasiva: se limita a la inicialización del árbol de 
    widgets y la renderización en pantalla de los datos metrológicos.

    Note:
        Delega toda la lógica de negocio, manejo de eventos de hardware y actualización 
        de estados al presentador principal (:class:`presenter.MainPresenter`).
    """
    def __init__(self) -> None:
        """Inicializa el ciclo de vida de la ventana principal y construye la interfaz.

        Ejecuta internamente el método ``setupUi(self)`` heredado para procesar e instanciar 
        los componentes gráficos (botones, lienzos de gráficas, etiquetas) definidos en la 
        plantilla estática. Esta inicialización ocurre de forma síncrona en el hilo 
        principal de la aplicación.
        """
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Instanciar la ventana compilada.
    window = MainWindow()

    # Instanciar los componentes del backend.
    oscilloscope = GWInstekGDS1000AU()
    file_system = FileManager()

    # Iniciar el Presentador (Vista - Modelo).
    app_presenter = MainPresenter(window, oscilloscope, file_system, LightningImpulseAnalyzer)

    # Mostrar y ejecutar.
    window.show()
    sys.exit(app.exec())