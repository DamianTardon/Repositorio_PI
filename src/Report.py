import numpy as np
import matplotlib.pyplot as plt

def print_information_TDG(metadata, data):
    print(f"Versión de TDG: {metadata['software_version']}")
    print(f"Versión de archivo de datos: {metadata['version_file']}")
    print(f"Nombre de onda: {metadata['wave_name']}")
    print(f"Resolución de datos: {metadata['resolution']}")
    print(f"Cantidad de muestras: {metadata['samples']}")
    print(f"Intervalo de muestreo: {metadata['interval']}")
    print(f"Tasa de muestreo: {metadata['rate']}")
    print("Datos de la onda:")
    print(f"\nTotal de puntos extraídos: {len(data)}")

def plot_1_waveform(time_axis1, waveform1, label1, title):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis1, waveform1, label=label1)
    plt.title(title)
    plt.legend()
    plt.xlabel("Tiempo [µs]")
    plt.ylabel("Tensión [kV]")
    plt.grid(True)
    plt.show()

def plot_2_waveform(time_axis1, waveform1, label1, time_axis2, waveform2, label2, title):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis1, waveform1, label=label1)
    plt.plot(time_axis2, waveform2, color='red',label=label2)
    plt.title(title)
    plt.legend()
    plt.xlabel("Tiempo [µs]")
    plt.ylabel("Tensión [kV]")
    plt.grid(True)
    plt.show()