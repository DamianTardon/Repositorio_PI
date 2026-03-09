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

def plot_recorded_curve(time_axis, recorded_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, recorded_curve)
    plt.title("Curva Registrada Original")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.grid(True)
    plt.show()

def plot_offset_compensated_curve(time_axis, offset_compensated_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, offset_compensated_curve)
    plt.title("Curva Registrada Compensada en Offset")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.grid(True)
    plt.show()

def plot_normalized_curve(time_axis, normalized_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, normalized_curve)
    plt.title("Curva de Polaridad Normalizada")
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
    plt.title("Curva Recortada para Ajuste")
    plt.legend()
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.grid(True)
    plt.show()

def plot_fitting_signal(time_cutted, cutted_signal, fitting_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_cutted, cutted_signal, '.', label='Datos para Ajuste')
    plt.plot(time_cutted, fitting_curve, 'r-', label='Ajuste Doble Exponencial')
    plt.title("Ajuste de Curva Base")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_base_curve(time_axis, original_signal, base_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, original_signal, label='Curva compensada en offset')
    plt.plot(time_axis, base_curve, 'r-', label='Curva Base')
    plt.title("Curva Base")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_residual_curve(time_axis, residual_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, residual_curve, label='Curva Residual')
    plt.title("Curva Residual")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_filtered_residual_curve(time_axis, filtered_residual):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, filtered_residual, label='Curva Residual Filtrada')
    plt.title("Curva Residual Filtrada")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_test_voltage_curve(time_axis, test_voltage_curve):
    plt.figure(figsize=(12, 3))
    plt.plot(time_axis, test_voltage_curve, label='Curva de Tensión de Ensayo')
    plt.title("Curva de Tensión de Ensayo")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Tensión [V]")
    plt.legend()
    plt.grid(True)
    plt.show()

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