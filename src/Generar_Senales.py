import numpy as np

# Señales de ejemplo para pruebas de manejo de archivos.
def generar_senales(dt):
    num_points = 4000
    time_axis = np.linspace(0, (num_points - 1) * dt, num_points)
    ch1 = np.sin(2 * np.pi * 1e5 * time_axis)
    # Convertir a binario int16 con escala 25 muestras/V
    ch1_bin = 25 * ch1
    ch1_bin = ch1_bin.astype('>i2').tobytes()
    return ch1_bin, ch1