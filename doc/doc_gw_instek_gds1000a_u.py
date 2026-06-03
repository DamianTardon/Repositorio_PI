from __future__ import annotations
import pyvisa
import numpy as np
from typing import Union, Tuple, Optional, Any

class GWInstekGDS1000AU:
    """Controlador de hardware vía interfaz SCPI/VISA para el osciloscopio digital GW Instek serie GDS-1000A-U.

    Proporciona una abstracción de alto nivel para gestionar la conexión USB/Ethernet, configuración de 
    parámetros de adquisición (escalas, trigger, offsets) y descarga de datos binarios masivos de la memoria
    interna del instrumento.

    Attributes:
        ADC_STEPS_PER_DIV (float): Constante geométrica de cuantización vertical del conversor ADC, 
            específica del hardware (típicamente 25.0 puntos por división).
        rm (pyvisa.ResourceManager): Gestor de recursos de PyVISA (backend '@py').
        dso (Optional[pyvisa.resources.Resource]): Instancia del objeto VISA que representa al instrumento activo.
    """

    ADC_STEPS_PER_DIV = 25.0

    def __init__(self) -> None:
        """Inicializa el backend VISA, escanea los puertos disponibles y autoconecta al primer recurso hallado."""
        ...

    def connect(self, resource_name: str) -> None:
        """Establece la conexión de datos con el instrumento dado su identificador de recurso.

        Configura los caracteres de terminación de línea y consulta la identificación estándar (`*IDN?`).

        Args:
            resource_name (str): Cadena de identificación del recurso VISA (ej. 'USB0::0x...::INSTR').
        """
        ...

    def get_block_data(self, channel: int) -> Tuple[Optional[bytes], Optional[np.ndarray], Optional[float]]:
        """Descarga la forma de onda completa desde la memoria de adquisición del osciloscopio.

        Comprueba si el estado de captura está listo. Luego, descarga el bloque de datos binarios
        por chunks, parsea el encabezado IEEE, y delega la reconstrucción matemática de la señal.

        Args:
            channel (int): Número de canal físico a descargar (1 o 2).

        Returns:
            Tuple[Optional[bytes], Optional[np.ndarray], Optional[float]]: 
                - Buffer crudo de bytes (`inBuffer`).
                - Vector de tensión de la onda en Voltios (`waveform`).
                - Periodo de muestreo temporal en segundos (`dt`).
                Retorna `(None, None, None)` en caso de error o si la onda no está lista.
        """
        ...

    def unpack_waveform(self, inBuffer: bytes, headerlen: int, vdiv: float) -> Tuple[np.ndarray, float]:
        """Decodifica el buffer de bytes IEEE en vectores matemáticos de tensión y tiempo.

        Extrae el periodo de muestreo temporal ($dt$) del encabezado flotante y convierte los datos 
        RAW de 16-bits a valores de tensión absoluta utilizando la constante geométrica del conversor ADC.
        Fórmula: 
            $$V = RAW \cdot \frac{V_{div}}{ADC_{steps}}$$

        Args:
            inBuffer (bytes): Cadena de bytes en bruto descargada vía VISA.
            headerlen (int): Longitud dinámica del encabezado SCPI de bloque.
            vdiv (float): Escala vertical actual del canal en V/div.

        Returns:
            Tuple[np.ndarray, float]: (Vector de tensiones de la onda `np.ndarray`, periodo de muestreo `float`).
        """
        ...

    def default_settings(self) -> None:
        """Restablece el osciloscopio a sus parámetros de fábrica mediante el comando SCPI `*RST`."""
        ...

    def get_setting(self) -> None:
        """Consulta e imprime por consola el string de configuración actual (`*LRN?`)."""
        ...

    def get_channel_scale(self, channel: int) -> Optional[float]:
        """Consulta la escala vertical activa de un canal.

        Args:
            channel (int): Identificador de canal (1 o 2).

        Returns:
            Optional[float]: Escala vertical en V/div.
        """
        ...

    def set_channel_scale(self, channel: int, value: float) -> None:
        """Configura la escala vertical (Voltage/Division) de un canal físico.

        Args:
            channel (int): Identificador de canal (1 o 2).
            value (float): Escala en V/div (ej. 5.0).
        """
        ...

    def get_timebase_scale(self) -> Optional[float]:
        """Consulta la escala de la base de tiempo global del instrumento.

        Returns:
            Optional[float]: Periodo de la base de tiempo en segundos/división.
        """
        ...

    def set_timebase_scale(self, value: float) -> None:
        """Configura la escala de la base de tiempo global (Time/Division).

        Args:
            value (float): Escala de tiempo en segundos/división.
        """
        ...

    def get_timebase_position(self) -> Optional[float]:
        """Consulta el desfase u offset horizontal global (Delay).

        Returns:
            Optional[float]: Posición horizontal temporal respecto al trigger en segundos.
        """
        ...

    def set_timebase_position(self, value: float) -> None:
        """Configura el desplazamiento u offset horizontal global (Delay).

        Args:
            value (float): Tiempo de desplazamiento en segundos.
        """
        ...

    def set_trigger(self, trigger_mode: str) -> None:
        """Envía una cadena SCPI en bruto para la configuración del trigger.

        Args:
            trigger_mode (str): Cadena de comando SCPI completa.
        """
        ...

    def get_trigger_level(self) -> Optional[float]:
        """Consulta el nivel absoluto de tensión utilizado como umbral de disparo.

        Returns:
            Optional[float]: Nivel de disparo en Voltios.
        """
        ...

    def set_trigger_level(self, trigger_level: float) -> None:
        """Establece el nivel de tensión de umbral para el disparo del osciloscopio.

        Args:
            trigger_level (float): Nivel absoluto de disparo en Voltios.
        """
        ...

    def get_trigger_coupling(self) -> Optional[str]:
        """Consulta el acoplamiento eléctrico del circuito de disparo.

        Returns:
            Optional[str]: 'AC' o 'DC'.
        """
        ...

    def set_trigger_coupling(self, coupling: int) -> None:
        """Configura el acoplamiento del circuito de disparo del osciloscopio.

        Args:
            coupling (int): 0 para 'AC', 1 para 'DC'.
        """
        ...

    def get_trigger_mode(self) -> Optional[str]:
        """Consulta el modo operacional de disparo activo.

        Returns:
            Optional[str]: 'Auto' o 'Normal'.
        """
        ...

    def set_trigger_mode(self, mode: int) -> None:
        """Configura el modo de adquisición ante eventos de disparo.

        Args:
            mode (int): 0 para 'Auto' (disparo iterativo), 1 para 'Normal'.
        """
        ...

    def get_trigger_nrej(self) -> Optional[str]:
        """Consulta el estado del filtro de rechazo de ruido acoplado al trigger.

        Returns:
            Optional[str]: 'OFF' o 'ON'.
        """
        ...

    def set_trigger_nrej(self, state: int) -> None:
        """Habilita o deshabilita el filtro de histéresis de rechazo de ruido de trigger.

        Args:
            state (int): 0 para 'OFF', 1 para 'ON'.
        """
        ...

    def get_trigger_reject(self) -> Optional[str]:
        """Consulta el filtro de frecuencia en el acople de disparo.

        Returns:
            Optional[str]: 'OFF', 'LF' (Low Frequency), o 'HF' (High Frequency).
        """
        ...

    def set_trigger_reject(self, mode: int) -> None:
        """Configura un filtro de corte de frecuencias específico en la etapa de disparo.

        Args:
            mode (int): 0 ('OFF'), 1 ('LF'), 2 ('HF').
        """
        ...

    def get_trigger_slope(self) -> Optional[str]:
        """Consulta el flanco del borde de disparo seleccionado.

        Returns:
            Optional[str]: 'Positivo' o 'Negativo'.
        """
        ...

    def set_trigger_slope(self, slope: int) -> None:
        """Configura el flanco sensitivo (borde) sobre el cual se evalúa el disparo.

        Args:
            slope (int): 0 para Flanco Positivo, 1 para Flanco Negativo.
        """
        ...

    def get_trigger_state(self) -> Optional[str]:
        """Monitorea el registro interno de estado del evento de captura del trigger.

        Returns:
            Optional[str]: 'No disparado' o 'Disparado'.
        """
        ...

    def get_trigger_source(self) -> Optional[str]:
        """Consulta el canal de origen desde donde se alimenta el circuito de disparo.

        Returns:
            Optional[str]: Fuente del trigger ('Canal 1', 'Canal 2', 'Externo', 'Red').
        """
        ...

    def set_trigger_source(self, source: int) -> None:
        """Asigna la entrada física como fuente para el evento de disparo.

        Args:
            source (int): Índice de hardware (0: 'CH1', 1: 'CH2', 2: 'EXT', 3: 'LINE').
        """
        ...

    def get_trigger_type(self) -> Optional[str]:
        """Consulta el tipo de topología de disparo configurado.

        Returns:
            Optional[str]: Topología ('Edge', 'Video', 'Pulse').
        """
        ...

    def set_trigger_type(self, ttype: int) -> None:
        """Configura la topología del evento de disparo.

        Args:
            ttype (int): Índice de la topología (0: 'Edge', 1: 'Video', 2: 'Pulse').
        """
        ...

    def get_acquire_mode(self) -> Optional[str]:
        """Consulta el modo de adquisición algorítmica y filtrado post-digitalización.

        Returns:
            Optional[str]: 'Normal', 'Peak detect', o 'Average'.
        """
        ...

    def set_acquire_mode(self, mode: int) -> None:
        """Configura la topología de muestreo y filtrado interno del instrumento.

        Args:
            mode (int): 0 ('Normal'), 1 ('Peak detect'), 2 ('Average').
        """
        ...

    def get_channel_coupling(self, channel: int) -> Optional[str]:
        """Consulta el filtro de acoplamiento de la entrada física de un canal analógico.

        Args:
            channel (int): Identificador de canal (1 o 2).

        Returns:
            Optional[str]: Tipo de acoplamiento eléctrico ('AC', 'DC', 'GND').
        """
        ...

    def set_channel_coupling(self, channel: int, coupling: int) -> None:
        """Configura el filtro de acoplamiento en la entrada analógica del hardware.

        Args:
            channel (int): Identificador de canal (1 o 2).
            coupling (int): Índice del filtro (0: 'AC', 1: 'DC', 2: 'GND').
        """
        ...

    def get_channel_display(self, channel: int) -> Optional[str]:
        """Consulta el estado de la renderización del canal en pantalla e interfaz interna.

        Args:
            channel (int): Identificador de canal (1 o 2).

        Returns:
            Optional[str]: 'ON' u 'OFF'.
        """
        ...

    def set_channel_display(self, channel: int, state: int) -> None:
        """Habilita o apaga un canal analógico específico del instrumento.

        Args:
            channel (int): Identificador de canal (1 o 2).
            state (int): 0 ('OFF'), 1 ('ON').
        """
        ...

    def get_channel_offset(self, channel: int) -> Optional[float]:
        """Consulta el desplazamiento vertical de visualización de tensión en un canal.

        Args:
            channel (int): Identificador de canal (1 o 2).

        Returns:
            Optional[float]: Voltaje de offset inyectado electrónicamente.
        """
        ...

    def set_channel_offset(self, channel: int, offset: float) -> None:
        """Configura el desplazamiento de inyección de tensión DC de un canal en pantalla.

        Args:
            channel (int): Identificador de canal (1 o 2).
            offset (float): Offset vertical en Voltios.
        """
        ...

    def get_channel_attenuation(self, channel: int) -> Optional[float]:
        """Consulta el factor de atenuación preconfigurado (Probe Ratio) de la punta del canal.

        Args:
            channel (int): Identificador de canal (1 o 2).

        Returns:
            Optional[float]: Ratio geométrico de la punta (ej. 1.0, 10.0).
        """
        ...

    def set_channel_attenuation(self, channel: int, attenuation: float) -> None:
        """Configura el multiplicador de escala interno (Probe Ratio) para una punta acoplada.

        Args:
            channel (int): Identificador de canal (1 o 2).
            attenuation (float): Factor numérico de atenuación (ej. 10 para punta x10).
        """
        ...

    def get_channel_type(self, channel: int) -> Optional[str]:
        """Consulta la magnitud física asociada lógicamente al canal.

        Args:
            channel (int): Identificador de canal (1 o 2).

        Returns:
            Optional[str]: 'Tensión' o 'Corriente'.
        """
        ...

    def set_channel_type(self, channel: int, ctype: int) -> None:
        """Configura la unidad y magnitud esperada en la entrada del instrumento.

        Args:
            channel (int): Identificador de canal (1 o 2).
            ctype (int): 0 para Voltaje ('Tensión'), 1 para Amperaje ('Corriente').
        """
        ...

    def set_single_trigger(self) -> None:
        """Arma el mecanismo de disparo para ejecutar una captura única (Single Sequence)."""
        ...

    def close(self) -> None:
        """Termina y libera jerárquicamente la interfaz de conexión VISA y el ResourceManager."""
        ...

    def __del__(self) -> None:
        """Destructor de la clase que asegura la liberación de recursos del SO invocando `close()`."""
        ...

    @staticmethod
    def process_multipliers(value: Union[str, float], unit: str) -> Optional[float]:
        """Procesa una cadena numérica combinada con una unidad para obtener una magnitud de ingeniería normalizada.

        Aplica factor de escala de manera agnóstica para transformar a unidades del SI estandarizadas
        (Voltios o Segundos).

        Args:
            value (Union[str, float]): Valor escalar como texto numérico o primitivo flotante.
            unit (str): Submúltiplo del SI ingresado ('V', 'mV', 'uV', 's', 'ms', 'µs', 'ns').

        Returns:
            Optional[float]: Valor absoluto escalado a unidad fundamental, o None si hay error sintáctico.
        """
        ...