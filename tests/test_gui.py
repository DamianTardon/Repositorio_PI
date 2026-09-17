import sys
import os
import pyqtgraph as pg
import pyqtgraph.exporters
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Importar los módulos de tu proyecto
from src.main import MainWindow
from src.gw_instek_gds1000a_u import GWInstekGDS1000AU
from src.file_manager import FileManager
from src.impulse_analyzer import LightningImpulseAnalyzer
from src.presenter import MainPresenter

# Rutas especificadas
BASE_PATH = r"C:\Users\Damian\Downloads"
WAVEFORM_FILE = os.path.join(BASE_PATH, "LI-A1.txt")

def run_automation():
    r"""Ejecuta la prueba automatizada de la GUI interactuando 
    programáticamente con los componentes de PySide6."""
    
    # Inicializar la aplicación de Qt
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Instanciar componentes del backend (hardware mock/real, sistema de archivos)
    oscilloscope = GWInstekGDS1000AU()
    file_system = FileManager()
    
    # Iniciar el Presentador
    presenter = MainPresenter(
        window, oscilloscope, file_system, LightningImpulseAnalyzer
    )
    
    window.show()
    print("Aplicación iniciada. Comenzando prueba automática...")

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
    
    # Configurar habilitadores de canal
    window.ch1_enabler.setChecked(True)
    window.ch2_enabler.setChecked(False)

    # Crear Carpeta de Ensayo
    # Parcheamos QFileDialog y QMessageBox para que no bloqueen la ejecución
    print(f"Creando carpeta de proyecto en: {BASE_PATH} ...")
    with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory', return_value=BASE_PATH), \
         patch('PySide6.QtWidgets.QMessageBox.information'), \
         patch('PySide6.QtWidgets.QMessageBox.question', return_value=65536): # 65536 es QMessageBox.Yes
        
        # Simulamos el clic en el botón de crear carpeta
        window.btn_create_folder.click()

    # Bucle de 5 iteraciones
    attenuator_start = 1.0
    
    for iteracion in range(5):
        # Calcular el valor del atenuador para esta iteración (1.0, 1.1, 1.2, 1.3, 1.4)
        current_att = attenuator_start + (iteracion * 0.1)
        print(f"\n--- Iteración {iteracion + 1}/5 ---")
        print(f"Modificando Atenuador (CH1) a: {current_att:.1f}")
        
        # Modificar el atenuador y emitir la señal para que el presentador lo registre
        window.ch1_attenuator_value.setText(f"{current_att:.1f}")
        window.ch1_attenuator_value.editingFinished.emit()
        
        # Cargar el archivo TXT
        print(f"Cargando archivo: {WAVEFORM_FILE} ...")
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=(WAVEFORM_FILE, "")), \
             patch('PySide6.QtWidgets.QMessageBox.critical'), \
             patch('PySide6.QtWidgets.QMessageBox.warning'):
            
            # Llamamos directamente a la función de carga por si DEBUG_MODE no estaba activo al arrancar
            presenter.load_tdg_waveform()
            
        # Guardar la onda
        print("Guardando onda en base de datos HDF5...")
        with patch('PySide6.QtWidgets.QMessageBox.information'), \
             patch('PySide6.QtWidgets.QMessageBox.warning'):
            
            window.btn_save_waveform.click()
            
        # Procesar eventos de Qt para que la UI se dibuje y actualice correctamente
        QApplication.processEvents()

    # Exportar el gráfico final
    print("\nGenerando imagen del gráfico final...")
    
    # Definir la ruta de salida para la imagen (dentro de la carpeta principal o base)
    project_folder = "1234-26 - LAT"
    graph_save_path = os.path.join(BASE_PATH, project_folder, "03 Resultados", "grafico_final.png")
    
    # Asegurar que la carpeta de resultados existe (por si acaso el FileManager la crea diferida)
    os.makedirs(os.path.dirname(graph_save_path), exist_ok=True)
    
    # Usar el exportador nativo de PyQtGraph
    exporter = pyqtgraph.exporters.ImageExporter(window.graph_view.plotItem)
    exporter.parameters()['width'] = 1920 # Forzar alta resolución
    exporter.export(graph_save_path)
    
    print(f"¡Éxito! Gráfico guardado en:\n{graph_save_path}")

    # Cerrar la aplicación automáticamente después de 3 segundos
    print("Cerrando prueba en 3 segundos...")
    QTimer.singleShot(3000, app.quit)

if __name__ == "__main__":
    run_automation()
    sys.exit()