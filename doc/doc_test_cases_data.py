"""Módulo de almacenamiento de vectores globales estáticos e ideales de prueba (Datasets de Calibración).

Define estructuras inmutables conteniendo las tablas maestras de datos analíticos
extraídas directamente de los anexos normativos de referencia A y B de la norma IEC 61083-2.

.. note::
    **Diseño de Instanciación:** La carga de datos se realiza mediante un flujo de dos etapas:
    primero se definen las tablas de tuplas crudas (Raw Data) estáticas y luego se instancian 
    dinámicamente como colecciones de objetos inmutables empleando *list comprehensions* y el desempaquetado de argumentos (``*row``).
    
    **Uso normativo de NaN:** En las tablas correspondientes a impulsos cortados (LIC), 
    se inyecta intencionalmente el valor ``NaN`` (Not a Number) para aquellos parámetros 
    (como el tiempo de frente :math:`T_1`) que, por diseño estricto de la norma, no son evaluables 
    ni aplican a la clasificación de dicha onda. Actúa como un mecanismo de exclusión seguro.
"""
from __future__ import annotations

from typing import NamedTuple, List, Tuple
import numpy as np

#: Constante estándar global predefinida que representa magnitudes irreales o métricas excluidas por norma.
nan: float = np.nan

#: Tupla base de empaquetado para tablas RAW de impulsos, simplificada para evitar verbosidad extrema en el tipado.
RawImpulseTuple = Tuple[str, str, float, float, float, float, float, float, float, float]

#: Tupla base de empaquetado para tablas RAW de incertidumbre algorítmica.
RawUncertaintyTuple = Tuple[str, float, float, int, float, float, int, float, float, int, float, float, int]

class ImpulseCase(NamedTuple):
    """Plantilla de estructuración para casos de test unitarios determinísticos de impulsos.
    
    Mapea los valores de referencia teóricos y las tolerancias normativas derivadas del Anexo A 
    de la IEC 61083-2, para la certificación de algoritmos de procesamiento de impulsos.

    .. important::
        **Inmutabilidad:** Al heredar de ``NamedTuple``, esta estructura garantiza que la 
        base de datos instanciada en memoria sea de estricta lectura (inmutable), previniendo 
        así cualquier alteración accidental de las tolerancias normativas durante la ejecución.

    Attributes:
        file_id (str): Identificador unívoco del caso de prueba (ej. 'LI-A1', 'LIC-M4').
        description (str): Detalle sintético descriptivo de las características físicas de la onda.
        U_reference (float): Magnitud de tensión pico teórica de referencia expresada en :math:`\unit{\kilo\volt}`.
        U_tolerance (float): Tolerancia porcentual simétrica admitida para la tensión pico en :math:`\unit{\percent}`.
        T1_reference (float): Tiempo de frente nominal esperado medido en :math:`\unit{\micro\second}`.
        T1_tolerance (float): Tolerancia porcentual admisible en la validación del frente en :math:`\unit{\percent}`.
        T2_reference (float): Parámetro temporal secundario en :math:`\unit{\micro\second}`. **Nota de dualidad:** En impulsos plenos (LI) representa el *Tiempo de Cola* (:math:`T_2`), mientras que en impulsos 
            cortados (LIC) muta semánticamente para representar el *Tiempo de Corte* (:math:`T_c`).
        T2_tolerance (float): Cota de dispersión porcentual admitida para la cola o el corte en :math:`\unit{\percent}`.
        OS_reference (float): Coeficiente de sobrepasamiento de tensión nominal esperado en :math:`\unit{\percent}`.
        OS_tolerance (float): Tolerancia absoluta permitida para el cálculo de sobrepasamiento en :math:`\unit{\percent}`.
    """
    file_id: str
    description: str

    U_reference: float
    U_tolerance: float

    T1_reference: float
    T1_tolerance: float

    T2_reference: float
    T2_tolerance: float

    OS_reference: float
    OS_tolerance: float

class UncertaintyCase(NamedTuple):
    """Consolida las cotas estándar de incertidumbre expandida normativas fijadas por laboratorios internacionales.

    Mapea los valores medios (:math:`\\bar{x}`), la incertidumbre expandida (:math:`U_x`) al 95% de confianza 
    y el número de observaciones estocásticas (:math:`n`) procedentes del Anexo B de la IEC 61083-2.

    .. important::
        Estructura inmutable (solo lectura) protegida por herencia de ``NamedTuple``.

    Attributes:
        file_id (str): Identificador unívoco de la onda analizada.
        U_reference (float): Valor medio del parámetro pico (:math:`U_t`) en :math:`\unit{\kilo\volt}`.
        U_ux (float): Incertidumbre expandida relativa (:math:`U_x`) para el valor pico en :math:`\unit{\percent}`.
        U_n (int): Cantidad de observaciones (:math:`n`) del valor pico.
        T1_reference (float): Valor medio del tiempo de frente (:math:`T_1`) en :math:`\unit{\micro\second}`.
        T1_ux (float): Incertidumbre expandida relativa (:math:`U_x`) para el frente en :math:`\unit{\percent}`.
        T1_n (int): Cantidad de observaciones (:math:`n`) del tiempo de frente.
        T2_reference (float): Valor medio temporal secundario en :math:`\unit{\micro\second}`. **Nota de dualidad:** Representa el *Tiempo de Cola* (:math:`T_2`) para ondas plenas o el *Tiempo de Corte* (:math:`T_c`) para cortadas.
        T2_ux (float): Incertidumbre expandida relativa (:math:`U_x`) para la cola/corte en :math:`\unit{\percent}`.
        T2_n (int): Cantidad de observaciones (:math:`n`) del tiempo de cola/corte.
        OS_reference (float): Valor medio del sobrepasamiento (:math:`OS` o :math:`\\beta'`) en :math:`\unit{\percent}`.
        OS_ux (float): Incertidumbre expandida absoluta (:math:`U_x`) para el sobrepasamiento en :math:`\unit{\percent}`.
        OS_n (int): Cantidad de observaciones (:math:`n`) del sobrepasamiento.
    """
    file_id: str

    U_reference: float
    U_ux: float
    U_n: int

    T1_reference: float
    T1_ux: float
    T1_n: int

    T2_reference: float
    T2_ux: float
    T2_n: int

    OS_reference: float
    OS_ux: float
    OS_n: int

# --- TABLAS NORMATIVAS CRUDAS (RAW DATA) ---
# Se omite el código fuente literal de las matrices de datos para priorizar la firma documental.

#: Tabla A.1 de IEC 61083-2: Full Lightning Impulses (LI).
RAW_TABLE_A1_LI: List[RawImpulseTuple] = ...

#: Tabla A.2 de IEC 61083-2: Chopped Lightning Impulses (LIC).
RAW_TABLE_A2_LIC: List[RawImpulseTuple] = ...

#: Tabla B.1 de IEC 61083-2: Expanded uncertainties (Ux) of LI reference values.
RAW_TABLE_B1_LI: List[RawUncertaintyTuple] = ...

#: Tabla B.2 de IEC 61083-2: Expanded uncertainties (Ux) of LIC reference values.
RAW_TABLE_B2_LIC: List[RawUncertaintyTuple] = ...


# --- INSTANCIACIÓN DE COLECCIONES LISTAS PARA VALIDACIÓN MATEMÁTICA ---
# Empaquetado dinámico convirtiendo tuplas crudas en objetos inmutables mediante *list comprehensions*.

#: Colección de casos de prueba instanciados para impulsos plenos.
TEST_CASES_LI: List[ImpulseCase] = ...

#: Colección de casos de prueba instanciados para impulsos cortados.
TEST_CASES_LIC: List[ImpulseCase] = ...

#: Colección de casos de incertidumbre instanciados para impulsos plenos.
UNCERTAINTY_CASES_LI: List[UncertaintyCase] = ...

#: Colección de casos de incertidumbre instanciados para impulsos cortados.
UNCERTAINTY_CASES_LIC: List[UncertaintyCase] = ...