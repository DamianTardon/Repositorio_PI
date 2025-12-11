import numpy as np
import matplotlib.pyplot as plt

def print_information(metadata, data):
    print(f"Versión de TDG: {metadata['sotfware_version']}")
    print(f"Versión de archivo de datos: {metadata['version_file']}")
    print(f"Nombre de onda: {metadata['wave_name']}")
    print(f"Resolución de datos: {metadata['resolution']}")
    print(f"Cantidad de muestras: {metadata['samples']}")
    print(f"Intervalo de muestreo: {metadata['interval']}")
    print(f"Tasa de muestreo: {metadata['rate']}")
    print("Datos de la onda:")
    print(f"\nTotal de puntos extraídos: {len(data)}")
    if False:
        for d in data:
            print(d)

def plot_waveform(waveform, dt):
    num_points = len(waveform)
    time_axis = np.linspace(0, (num_points - 1) * dt, num_points)
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, waveform)
    plt.title("Forma de Onda Adquirida")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.grid(True)
    plt.show()

def plot_waveform_2(waveform, time_axis):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, waveform)
    plt.title("Forma de Onda Adquirida")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.grid(True)
    plt.show()

def plot_cutting_signal(time_axis, original_signal, time_cutted, cutted_signal):
    plt.figure(figsize=(12, 3))
    # 1. Onda completa.
    plt.plot(time_axis, original_signal, color='red', label='Onda Completa')
    # 2. Parte recortada (sobrepuesta).
    plt.plot(time_cutted, cutted_signal, label='Datos para Ajuste (0.2 a 0.4)')
    plt.title("Validación de Recorte")
    plt.legend()
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.grid(True)
    plt.show()