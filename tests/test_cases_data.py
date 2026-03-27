from typing import NamedTuple
import numpy as np

nan = np.nan

class ImpulseCase(NamedTuple):
    file_id: str             # Nombre de la onda.
    description: str         # Descripción de la onda.

    # Valor Pico (U)
    U_reference: float       # Valor esperado.
    U_tolerance: float       # Tolerancia.

    # Tiempo de Frente (T1)
    T1_reference: float      # Valor esperado.
    T1_tolerance: float      # Tolerancia.

    # Tiempo de Cola (T2)
    T2_reference: float      # Valor esperado.
    T2_tolerance: float      # Tolerancia.

    # Sobrepasamiento (Beta')
    OS_reference: float      # Valor esperado.
    OS_tolerance: float      # Tolerancia.

class UncertaintyCase(NamedTuple):
    file_id: str             # Nombre de la onda.

    # Valor Pico (U).
    U_reference: float       # Valor medio (kV).
    U_ux: float              # Incertidumbre Expandida Ux (%).
    U_n: int                 # Número de observaciones (n).

    # Tiempo de Frente (T1).
    T1_reference: float      # Valor medio (µs).
    T1_ux: float             # Incertidumbre Expandida Ux (%).
    T1_n: int                # Número de observaciones (n).

    # Tiempo de Cola (T2).
    T2_reference: float      # Valor medio (µs).
    T2_ux: float             # Incertidumbre Expandida Ux (%).
    T2_n: int                # Número de observaciones (n).

    # Sobrepasamiento (Beta').
    OS_reference: float      # Valor medio (%).
    OS_ux: float             # Incertidumbre Expandida Ux (Absoluta %).
    OS_n: int                # Número de observaciones (n).

# TABLA A.1 (Full Lightning Impulse).
RAW_TABLE_A1_LI = [
    ("LI-A1", "Superposition of two ideal exponential functions", 1049.60, 0.10, 0.840, 2.0, 60.16, 1.0, 0.0, 1.0),
    ("LI-A2", "Slow oscillations", 1037.60, 0.10, 1.693, 2.0, 47.48, 1.0, 5.1, 1.0),
    ("LI-A3", "Fast oscillations", 1000.20, 0.10, 1.117, 2.0, 48.15, 1.0, 4.6, 1.0),
    ("LI-A4", "f = 500 kHz Overshoot 8%", 856.01, 0.10, 0.841, 2.0, 47.80, 1.0, 7.9, 1.0),
    ("LI-A5", "f = 200 kHz Overshoot 8%", 71.972, 0.10, 1.711, 2.0, 47.71, 1.0, 7.7, 1.0),
    ("LI-A6", "f = 200 kHz Overshoot 18%", 100.17, 0.10, 1.762, 2.0, 41.58, 1.0, 17.7, 1.0),
    ("LI-A7", "f = 200 kHz Overshoot 20%", 104.35, 0.10, 2.122, 2.0, 38.36, 1.0, 20.1, 1.0),
    ("LI-A8", "f = 250 kHz Overshoot 15%", 96.012, 0.10, 1.503, 2.0, 44.92, 1.0, 14.8, 1.0),
    ("LI-A9", "f = 300 kHz Overshoot 4%", 55.928, 0.10, 1.215, 2.0, 55.74, 1.0, 4.0, 1.0),
    ("LI-A10", "f = 400 kHz Overshoot 12%", 81.929, 0.10, 0.924, 2.0, 42.66, 1.0, 12.0, 1.0),
    ("LI-A11", "f = 800 kHz Overshoot 4%", 86.597, 0.10, 0.578, 2.0, 56.37, 1.0, 4.1, 1.0),
    ("LI-A12", "f = 900 kHz Overshoot 2%", 85.584, 0.10, 0.587, 2.0, 57.36, 1.0, 2.3, 1.0),
    ("LI-M1", "Front oscillations", 952.09, 0.10, 1.123, 2.0, 85.60, 1.0, 2.1, 1.0),
    ("LI-M2", "Long duration overshoot", -1041.70, 0.10, 3.356, 2.0, 61.25, 1.0, 9.2, 1.0),
    ("LI-M3", "Short duration overshoot", -1026.50, 0.10, 2.150, 2.0, 41.75, 1.0, 9.2, 1.0),
    ("LI-M4", "Oscillations, transformer testing", -267.14, 0.10, 0.987, 2.0, 56.22, 1.0, 4.8, 1.0),
    ("LI-M5", "Oscillations, transformer testing", -55.003, 0.10, 2.746, 2.0, 42.11, 1.0, 18.7, 1.0),
    ("LI-M6", "Oscillations, transformer testing", -166.87, 0.10, 1.356, 2.0, 54.74, 1.0, 3.8, 1.0),
    ("LI-M7", "Oscillations, transformer testing", -1272.30, 0.10, 1.482, 2.0, 50.03, 1.0, 11.2, 1.0),
    ("LI-M8", "Long front, smooth", -99.732, 0.10, 1.515, 2.0, 49.36, 1.0, -0.5, 1.0),
    ("LI-M9", "Short front, some overshoot", -100.04, 0.10, 0.828, 2.0, 46.65, 1.0, 1.4, 1.0),
    ("LI-M10", "Heavy front oscillations", 100.26, 0.10, 1.666, 2.0, 60.85, 1.0, 0.0, 1.0),
    ("LI-M11", "Heavy front oscillations", 299.32, 0.10, 1.661, 2.0, 60.95, 1.0, -0.5, 1.0),
    ("LI-M12", "Changing offset level, oscillations at peak", -4.3193, 0.10, 1.292, 2.0, 52.27, 1.0, -1.8, 1.0),
    ("LI-M13", "Oscillations after onset", 39.460, 0.10, 1.537, 2.0, 46.94, 1.0, 1.8, 1.0),
    ("LI-M14", "Oscillations after onset, and overshoot", 48.549, 0.10, 0.933, 2.0, 37.48, 1.0, 4.3, 1.0),
    ("LI-M15", "Oscillations after onset, and overshoot", 497.97, 0.10, 1.017, 2.0, 59.19, 1.0, -0.1, 1.0),
    ("LI-M16", "Front oscillations", 369.21, 0.10, 0.920, 2.0, 47.53, 1.0, 0.8, 1.0),
    ("LI-M17", "Heavy oscillations at front and peak", -99.346, 0.10, 1.775, 2.0, 53.31, 1.0, 1.3, 1.0)
]

# TABLA A.2 (Chopped Lightning Impulse - LIC).
RAW_TABLE_A2_LIC = [
    ("LIC-A1", "Front chopped lightning impulse", 872.2, 1.0, nan, nan, 0.543, 2.0, nan, nan),
    ("LIC-M1", "Front oscillations, chopped ", 850.0, 1.0, nan, nan, 0.569, 2.0, nan, nan),
    ("LIC-M2", "Front chopped", 0.289, 1.0, nan, nan, 0.514, 2.0, nan, nan),
    ("LIC-M3", "Front chopped", -0.3036, 1.0, nan, nan, 0.568, 2.0, nan, nan),
    ("LIC-M4", "Tail chopped", 0.1478, 1.0, 1.305, 2.0, 6.00, 2.0, -0.2, 1.0),
    ("LIC-M5", "Tail chopped", -389.9, 1.0, 0.857, 2.0, 9.24, 2.0, 6.8, 1.0)
]

# TABLA B.1 - (Expanded uncertainties (Ux) of the lightning impulse reference values).
RAW_TABLE_B1_LI = [
    # file_id, U_x, U_ux, U_n, T1_x, T1_ux, T1_n, T2_x, T2_ux, T2_n, beta_x, beta_ux, beta_n
    ("LI-A1", 1049.60, 0.002, 8, 0.83984, 0.011, 8, 60.156, 0.003, 8, 0.001, 0.003, 5),
    ("LI-A2", 1037.63, 0.008, 8, 1.693, 0.12, 8, 47.479, 0.011, 8, 5.14, 0.02, 7),
    ("LI-A3", 1000.2, 0.02, 8, 1.117, 0.3, 8, 48.15, 0.04, 8, 4.575, 0.007, 7),
    ("LI-A4", 856.01, 0.005, 8, 0.841, 0.3, 8, 47.802, 0.012, 8, 7.88, 0.02, 7),
    ("LI-A5", 71.972, 0.006, 8, 1.711, 0.3, 8, 47.705, 0.02, 8, 7.74, 0.05, 7),
    ("LI-A6", 100.170, 0.005, 8, 1.762, 0.4, 8, 41.576, 0.02, 8, 17.73, 0.02, 7),
    ("LI-A7", 104.349, 0.011, 8, 2.122, 0.5, 8, 38.36, 0.04, 8, 20.15, 0.07, 7),
    ("LI-A8", 96.012, 0.009, 8, 1.503, 0.3, 8, 44.924, 0.02, 8, 14.75, 0.03, 7),
    ("LI-A9", 55.928, 0.007, 8, 1.2152, 0.12, 8, 55.737, 0.015, 8, 4.02, 0.02, 7),
    ("LI-A10", 81.929, 0.009, 8, 0.924, 0.4, 8, 42.659, 0.02, 8, 12.01, 0.05, 7),
    ("LI-A11", 86.597, 0.004, 8, 0.578, 0.3, 8, 56.367, 0.009, 8, 4.066, 0.010, 7),
    ("LI-A12", 85.584, 0.004, 8, 0.5874, 0.2, 8, 57.358, 0.009, 8, 2.267, 0.007, 7),
    ("LI-M1", 952.09, 0.007, 8, 1.123, 0.4, 8, 85.603, 0.02, 8, 2.082, 0.003, 7),
    ("LI-M2", -1041.7, 0.015, 8, 3.356, 0.09, 8, 61.249, 0.006, 8, 9.18, 0.02, 7),
    ("LI-M3", -1026.5, 0.02, 8, 2.150, 0.13, 8, 41.749, 0.015, 8, 9.17, 0.02, 7),
    ("LI-M4", -267.14, 0.03, 7, 0.987, 0.4, 6, 56.22, 0.06, 7, 4.82, 0.02, 5),
    ("LI-M5", -55.003, 0.010, 8, 2.746, 0.4, 8, 42.11, 0.05, 8, 18.71, 0.08, 7),
    ("LI-M6", -166.865, 0.005, 8, 1.3556, 0.02, 8, 54.739, 0.007, 8, 3.837, 0.014, 7),
    ("LI-M7", -1272.3, 0.02, 8, 1.482, 0.3, 8, 50.03, 0.05, 8, 11.20, 0.04, 7),
    ("LI-M8", -99.732, 0.004, 8, 1.5147, 0.08, 8, 49.358, 0.004, 8, -0.55, 0.02, 7),
    ("LI-M9", -100.035, 0.006, 8, 0.8283, 0.08, 8, 46.654, 0.02, 8, 1.382, 0.007, 7),
    ("LI-M10", 100.258, 0.004, 8, 1.666, 0.09, 8, 60.853, 0.003, 8, -0.007, 0.011, 6),
    ("LI-M11", 299.324, 0.004, 8, 1.6611, 0.07, 8, 60.946, 0.005, 8, -0.457, 0.002, 7),
    ("LI-M12", -4.3193, 0.008, 8, 1.292, 0.2, 8, 52.266, 0.011, 8, -1.76, 0.05, 7),
    ("LI-M13", 39.460, 0.0048, 8, 1.537, 0.2, 8, 46.937, 0.013, 8, 1.763, 0.014, 7),
    ("LI-M14", 48.549, 0.012, 8, 0.933, 0.2, 7, 37.479, 0.04, 8, 4.27, 0.04, 7),
    ("LI-M15", 497.97, 0.005, 8, 1.0166, 0.11, 8, 59.187, 0.007, 8, -0.08, 0.02, 7),
    ("LI-M16", 369.21, 0.005, 8, 0.9198, 0.10, 8, 47.531, 0.010, 8, 0.833, 0.006, 7),
    ("LI-M17", -99.346, 0.003, 8, 1.7747, 0.04, 7, 53.3124, 0.002, 8, 1.327, 0.003, 7)
]

# TABLA B.2 - (Expanded uncertainties (Ux) of the chopped lightning impulse reference values).
# En los impulsos cortados, T2 representa el Tiempo de Corte (Tc o Td).
RAW_TABLE_B2_LIC = [
    # file_id, U_x, U_ux, U_n, T1_x, T1_ux, T1_n, Tc_x, Tc_ux, Tc_n, beta_x, beta_ux, beta_n
    ("LIC-A1", 872.21, 0.005, 5, nan, nan, 0, 0.54301, 0.005, 5, nan, nan, 0),
    ("LIC-M1", 850.0, 0.07, 5, nan, nan, 0, 0.5691, 0.12, 5, nan, nan, 0),
    ("LIC-M2", 0.28903, 0.02, 5, nan, nan, 0, 0.514, 0.4, 5, nan, nan, 0),
    ("LIC-M3", -0.30360, 0.02, 4, nan, nan, 0, 0.5679, 0.2, 5, nan, nan, 0),
    ("LIC-M4", 0.14781, 0.03, 6, 1.305, 0.6, 6, 6.00, 0.3, 6, -0.16, 0.05, 5),
    ("LIC-M5", -389.9, 0.05, 6, 0.857, 0.9, 5, 9.24, 0.2, 6, 6.85, 0.04, 5)
]

# Listas separadas para los tests.
TEST_CASES_LI = [ImpulseCase(*row) for row in RAW_TABLE_A1_LI]
TEST_CASES_LIC = [ImpulseCase(*row) for row in RAW_TABLE_A2_LIC]
UNCERTAINTY_CASES_LI = [UncertaintyCase(*row) for row in RAW_TABLE_B1_LI]
UNCERTAINTY_CASES_LIC = [UncertaintyCase(*row) for row in RAW_TABLE_B2_LIC]