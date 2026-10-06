from pathlib import Path
from typing import Optional, Union
import numpy as np
import matplotlib.pyplot as plt

def print_information(metadata, data):
    print(f"Versión de TDG: {metadata['software_version']}")
    print(f"Versión de archivo de datos: {metadata['version_file']}")
    print(f"Nombre de onda: {metadata['wave_name']}")
    print(f"Resolución de datos: {metadata['resolution']}")
    print(f"Cantidad de muestras: {metadata['samples']}")
    print(f"Intervalo de muestreo: {metadata['interval']}")
    print(f"Tasa de muestreo: {metadata['rate']}")
    print("Datos de la onda:")
    print(f"\nTotal de puntos extraídos: {len(data)}")

def plot_1_waveform(time_axis1: np.ndarray, waveform1: np.ndarray, label1: str, 
                    title: str, save_path: Optional[Union[str, Path]] = None) -> None:
    """Grafica una única forma de onda y permite su exportación.

    Args:
        time_axis1 (np.ndarray): Vector de tiempo.
        waveform1 (np.ndarray): Vector de amplitud de tensión.
        label1 (str): Etiqueta de la curva para la leyenda.
        title (str): Título principal del gráfico.
        save_path (Optional[Union[str, Path]]): Ruta absoluta o relativa para 
            exportar la imagen. Si es None, no se exporta.
    """
    plt.figure(figsize=(12, 5), dpi=100)
    plt.plot(time_axis1, waveform1, color="#3191cc", linewidth=2, label=label1)
    plt.title(title)
    plt.legend()
    plt.xlabel("Tiempo [µs]")
    plt.ylabel("Tensión [kV]")
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', format='png')
    
    plt.show()


def plot_2_waveform(time_axis1: np.ndarray, waveform1: np.ndarray, label1: str, 
                    time_axis2: np.ndarray, waveform2: np.ndarray, label2: str, 
                    title: str, save_path: Optional[Union[str, Path]] = None) -> None:
    """Grafica dos formas de onda superpuestas y permite su exportación.

    Args:
        time_axis1 (np.ndarray): Vector de tiempo de la primera curva.
        waveform1 (np.ndarray): Vector de amplitud de la primera curva.
        label1 (str): Etiqueta de la primera curva.
        time_axis2 (np.ndarray): Vector de tiempo de la segunda curva.
        waveform2 (np.ndarray): Vector de amplitud de la segunda curva.
        label2 (str): Etiqueta de la segunda curva.
        title (str): Título principal del gráfico.
        save_path (Optional[Union[str, Path]]): Ruta absoluta o relativa para 
            exportar la imagen. Si es None, no se exporta.
    """
    plt.figure(figsize=(12, 5), dpi=100)
    plt.plot(time_axis1, waveform1, color="#3191cc", linewidth=2, label=label1)
    plt.plot(time_axis2, waveform2, color='red', linewidth=2, label=label2)
    plt.title(title)
    plt.legend()
    plt.xlabel("Tiempo [µs]")
    plt.ylabel("Tensión [kV]")
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', format='png')
        
    plt.show()