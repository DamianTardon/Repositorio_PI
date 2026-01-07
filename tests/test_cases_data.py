from typing import NamedTuple
#import pytest
#import math

# 1. Definición de la estructura
class ImpulseCase(NamedTuple):
    file_id: str
    description: str
    expected_peak: float
    tolerance_peak: float
    expected_T1: float
    tolerance_T1: float
    expected_T2: float
    tolerance_T2: float
    expected_beta: float
    tolerance_beta: float

# 2. Datos Crudos (Raw Data) - IEC 61083-2
# TABLA A.1 (Full Lightning Impulse)
# (ID, Descripcion, Ut, Ut%, T1, T1%, T2, T2%, Beta, Beta%)
RAW_DATA_LI = [
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

# TABLA A.2 (Chopped Lightning Impulse - LIC)
# (ID, Descripcion, Up, Up%, T1, T1%, Tc, Tc%, Beta, Beta%)
nan = float('nan')
RAW_DATA_LIC = [
    ("LIC-A1", "Front chopped lightning impulse", 872.2, 1.0, nan, nan, 0.543, 2.0, nan, nan),
    ("LIC-M1", "Front oscillations, chopped ", 850.0, 1.0, nan, nan, 0.569, 2.0, nan, nan),
    ("LIC-M2", "Front chopped", 0.289, 1.0, nan, nan, 0.514, 2.0, nan, nan),
    ("LIC-M3", "Front chopped", -0.3036, 1.0, nan, nan, 0.568, 2.0, nan, nan),
    ("LIC-M4", "Tail chopped", 0.1478, 1.0, 1.305, 2.0, 6.00, 2.0, -0.2, 1.0),
    ("LIC-M5", "Tail chopped", -389.9, 1.0, 0.857, 2.0, 9.24, 2.0, 6.8, 1.0)
]

# 3. Generación automática de TEST_CASES
TEST_CASES = []

# Full Impulse (LI)
for row in RAW_DATA_LI:
    TEST_CASES.append(ImpulseCase(
        file_id=f"{row[0]}.txt",
        description=row[1],
        expected_peak=row[2],
        tolerance_peak=row[3],
        expected_T1=row[4],
        tolerance_T1=row[5],
        expected_T2=row[6],
        tolerance_T2=row[7],
        expected_beta=row[8],
        tolerance_beta=row[9]
    ))

# Chopped Impulse (LIC)
# NOTA: Para LIC, T2 = Tc (Tiempo de corte)
for row in RAW_DATA_LIC:
    TEST_CASES.append(ImpulseCase(
        file_id=f"{row[0]}.txt",
        description=row[1],
        expected_peak=row[2],
        tolerance_peak=row[3],
        expected_T1=row[4],
        tolerance_T1=row[5],
        expected_T2=row[6],
        tolerance_T2=row[7],
        expected_beta=row[8],
        tolerance_beta=row[9]
    ))