import sys
import os
from unittest.mock import patch
from PySide6.QtWidgets import QApplication

# Importar los módulos de tu proyecto
from main import MainWindow
from gw_instek_gds1000a_u import GWInstekGDS1000AU
from file_manager import FileManager
from impulse_analyzer import LightningImpulseAnalyzer
from presenter import MainPresenter

# Ruta base especificada
BASE_PATH = r"C:\Users\Damian\Downloads"

def run_preload():
    r"""Ejecuta una precarga de datos en la GUI y cede el control al usuario."""
    
    # Inicializar la aplicación de Qt
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Instanciar componentes del backend (hardware, sistema de archivos)
    oscilloscope = GWInstekGDS1000AU()
    file_system = FileManager()
    
    # Iniciar el Presentador
    presenter = MainPresenter(
        window, oscilloscope, file_system, LightningImpulseAnalyzer
    )
    
    window.show()
    print("Aplicación iniciada. Precargando datos...")

    # Completar los campos de la interfaz
    print("Completando campos de texto...")
    window.item_number_value.setText("1234")
    window.item_year_value.setText("26")
    window.client_value.setText("LAT")
    
    window.db_temperature_value.setText("25.0")
    window.wb_temperature_value.setText("25.0")
    window.relative_humidity_value.setText("55.0")
    window.absolute_humidity_value.setText("55.0")
    window.pressure_value.setText("970.5")
    
    # Configurar habilitadores de canal y atenuación inicial
    window.ch1_enabler.setChecked(True)
    window.ch2_enabler.setChecked(False)
    window.ch1_attenuator_value.setText("1.0")

    # Crear Carpeta de Ensayo
    # Parcheamos QFileDialog y QMessageBox para que se cree silenciosamente
    print(f"Creando carpeta de proyecto en: {BASE_PATH} ...")
    
    with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory', return_value=BASE_PATH), \
         patch('PySide6.QtWidgets.QMessageBox.information'), \
         patch('PySide6.QtWidgets.QMessageBox.question', return_value=65536): # 65536 es QMessageBox.Yes
        
        # Simulamos el clic en el botón de crear carpeta
        window.btn_create_folder.click()

    # Forzar modo depuración para el botón "Iniciar"
    print("Forzando depuración: Vinculando botón 'Iniciar' a carga local (load_tdg_waveform)...")
    try:
        # Desconectamos la función original (receive_waveform)
        window.btn_wait_waveform.clicked.disconnect()
    except RuntimeError:
        pass # Ignorar si la señal no estaba conectada
    
    # Vinculamos a la función de carga manual de archivos
    window.btn_wait_waveform.clicked.connect(presenter.load_tdg_waveform)

    print(" Precarga finalizada.El proyecto fue creado.")
    print(" Continuar manualmente.")
    
    # Ceder el control al usuario
    sys.exit(app.exec())

if __name__ == "__main__":
    run_preload()