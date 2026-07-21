r"""Módulo de interfaz de hardware para el osciloscopio GW Instek de la 
serie GDS-1000A-U.

Este módulo encapsula todas las operaciones de control síncrono, 
configuración de canales, manipulación del sistema de disparo (trigger) 
y adquisición de datos binarios desde el osciloscopio mediante comandos 
SCPI sobre PyVISA.
"""

from __future__ import annotations

import time
from struct import unpack
import pyvisa
import numpy as np

# Importaciones exclusivas para el tipado estático en la documentación.
from typing import Optional, Tuple, Union


class GWInstekGDS1000AU:
    r"""Controlador programático para el osciloscopio digital GW Instek 
    de la serie GDS-1000A-U.

    Administra la apertura y cierre de sesiones VISA, el formateo de 
    comandos de escritura/lectura SCPI y la decodificación de tramas 
    binarias procedentes de la memoria interna del instrumento. 

    Note:
        La clase implementa un estricto mecanismo de protección 
        (failsafe): ante cualquier excepción de E/S o pérdida de 
        comunicación detectada en los métodos operativos, el error es 
        capturado internamente y se invoca automáticamente al método 
        :meth:`close` para asegurar la liberación del recurso VISA y 
        evitar bloqueos en el bus.

    Attributes:
        ADC_STEPS_PER_DIV (float): Constante de cuantización vertical 
            del conversor ADC, específica de la serie GW Instek 
            GDS-1000A-U (25 puntos por división).
        rm (pyvisa.ResourceManager): Gestor global de recursos de la 
            plataforma VISA (backend '@py').
        dso (Optional[pyvisa.resources.Resource]): Instancia del objeto 
            VISA que representa al instrumento activo.
    """

    ADC_STEPS_PER_DIV: float = 25.0
    r"""Constante de cuantización vertical del ADC de la serie 
    GW Instek GDS 1000AU.
    """

    def __init__(self) -> None:
        r"""Inicializa el gestor de recursos de PyVISA y busca 
        dispositivos compatibles.

        Intenta establecer una conexión automática con el primer 
        instrumento detectado en la lista de recursos activos del 
        sistema invocando a :meth:`connect`.
        """
        self.dso = None
        self.rm = pyvisa.ResourceManager('@py')

        try:
            instrument_list = self.rm.list_resources()
            print("Instrumentos encontrados:", instrument_list)
            if instrument_list:
                self.connect(instrument_list[0])
        except Exception as e:
            print("Error durante la inicialización del gestor VISA:", e)

    def connect(self, resource_name: str) -> None:
        r"""Establece la conexión física y lógica con el osciloscopio 
        especificado.

        Configura los caracteres de terminación de línea (``\n``) y 
        consulta la identificación estándar (``*IDN?``). En caso de 
        error en la comunicación, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            resource_name (str): Cadena de texto de dirección del 
                recurso VISA (ej. 'USB0::0x...::INSTR').
        """
        try:
            self.dso = self.rm.open_resource(resource_name)
            self.dso.read_termination = '\n'
            self.dso.write_termination = '\n'
            idn = self.dso.query('*IDN?')
            print("Instrumento conectado satisfactoriamente:", idn)
        except Exception as e:
            print("Error al iniciar con el instrumento:", e)
            self.close()

    def get_block_data(
            self, 
            channel: int
    ) -> Tuple[Optional[bytes], Optional[np.ndarray], Optional[float]]:
        r"""Adquiere el bloque binario completo de la forma de onda 
        activa en la memoria del canal.

        Gestiona el handshake SCPI comprobando el estado de captura y 
        solicitando el buffer de memoria. La lectura se particiona 
        iterativamente en fragmentos máximos de 
        :math:`\qty{100000}{\byte}` para evitar desbordamientos del bus 
        USB. En caso de error de lectura, captura la excepción, ejecuta 
        :meth:`close` y aborta la captura devolviendo valores nulos.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Tuple[Optional[bytes], Optional[np.ndarray], Optional[float]]: 
                Una tupla que contiene:
                - Buffer crudo de bytes (``in_buffer``).
                - Vector de tensión de la onda en 
                  :math:`\unit{\volt}` (``waveform``).
                - Periodo de muestreo temporal en 
                  :math:`\unit{\second}` (``dt``).
                Si la onda no está lista en el instrumento o falla la 
                comunicación, retorna ``(None, None, None)``.
        """
        if self.dso is None:
            print(
                "Error: No se puede obtener datos. "
                "El instrumento no está conectado."
            )
            return None, None, None

        try:
            v_div = self.get_channel_scale(channel)
            if v_div is None:
                return None, None, None

            self.dso.write(f':acquire{channel}:state?')
            state = self.dso.read()

            if state[0] == '1':
                time.sleep(0.1)
                self.dso.write(f":acquire{channel}:memory?")

                # Leer el encabezado inicial (10 bytes).
                in_buffer = self.dso.read_bytes(10)
                length = len(in_buffer)
                headerlen = 2 + int(chr(in_buffer[1]))
                pkg_length = int(in_buffer[2:headerlen]) + headerlen
                pkg_length = pkg_length - length

                while pkg_length > 0:
                    # Determinar tamaño de paquete de lectura.
                    chunk_size = min(pkg_length, 100000)

                    try:
                        buf = self.dso.read_bytes(chunk_size)
                    except Exception as e:
                        print(f"Error al recibir el bloque de datos: {e}")
                        raise RuntimeError(
                            "Fallo en la transferencia USB/VISA. "
                            "Bloque de datos perdido."
                        )

                    in_buffer += buf
                    pkg_length -= len(buf)

                waveform, dt = self.unpack_waveform(in_buffer, headerlen, v_div)
                return in_buffer, waveform, dt
            else:
                print('Error: Forma de onda aún no está lista.')
                return None, None, None
        except Exception as e:
            print("Error al obtener datos:", e)
            self.close()
            return None, None, None

    def unpack_waveform(
            self, 
            in_buffer: bytes, 
            headerlen: int, 
            vdiv: float
    ) -> Tuple[Optional[np.ndarray], Optional[float]]:
        r"""Decodifica el buffer de bytes IEEE en vectores matemáticos 
        de tensión y tiempo.

        Extrae el periodo de muestreo temporal (:math:`\text{dt}`) del 
        encabezado flotante y convierte los datos RAW de 16-bits a 
        valores de tensión absoluta utilizando la constante del 
        conversor ADC. Si ocurre un fallo en el desempaquetado o en el 
        cálculo, captura la excepción y retorna un par de nulos.

        .. math::

            V = \text{RAW} \cdot \frac{V_{\text{div}}}{\text{ADC}_{\text{steps}}}

        Args:
            in_buffer (bytes): Cadena de bytes en bruto descargada vía VISA.
            headerlen (int): Longitud dinámica calculada del encabezado 
                SCPI de bloque.
            vdiv (float): Escala vertical actual del canal en 
                :math:`\unit{\volt\per\text{div}}`.

        Returns:
            Tuple[Optional[np.ndarray], Optional[float]]: Una tupla que 
                contiene:
                - waveform (Optional[np.ndarray]): Vector de tensión de 
                  la onda en :math:`\unit{\volt}`, o ``None`` si se 
                  produce un fallo durante la conversión.
                - dt (Optional[float]): Periodo de muestreo temporal en 
                  :math:`\unit{\second}`, o ``None`` si se produce un 
                  fallo durante la conversión.
        """
        try:
            print(in_buffer[:headerlen])

            # Desempaquetado del periodo de muestreo dt 
            # (float de 4 bytes en Big-Endian).
            dt = unpack('>f', in_buffer[headerlen : headerlen + 4])[0]
            print(f'Periodo de muestreo = {dt*1e9:.0f} [ns]')

            # Extracción del segmento binario de la señal.
            raw_data = in_buffer[headerlen + 8:]
            # Conteo de muestras (short - 2 bytes).
            num_samples = int(len(raw_data) / 2)
            print(f'Cantidad de muestras = {num_samples}')

            # Desempaquetado dinámico del vector de muestras RAW.
            waveform_raw = unpack('>%sh' % num_samples, raw_data)
            waveform_raw = np.array(waveform_raw)

            # Escalamiento y normalización del vector binario 
            # a magnitudes físicas reales de tensión.
            waveform = waveform_raw * vdiv / self.ADC_STEPS_PER_DIV
            return waveform, dt
        except Exception as e:
            print("Error de decodificación de datos binarios:", e)
            return None, None

    def default_settings(self) -> None:
        r"""Restablece los registros internos del osciloscopio a sus 
        valores de fábrica (``*RST``).
        
        En caso de error en la comunicación, captura la excepción y 
        ejecuta :meth:`close`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write('*RST')
            print("Se restableció el instrumento a la "
                  "configuración de fábrica exitosamente.")
        except Exception as e:
            print("Error al restablecer el instrumento:", e)
            self.close()

    def get_channel_scale(self, channel: int) -> Optional[float]:
        r"""Consulta la escala vertical configurada en un canal 
        determinado.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Optional[float]: Valor de escala vertical en 
            :math:`\unit{\volt/\text{div}}`, o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        try:
            scale = self.dso.query(f':channel{channel}:scale?')
            v_scale = float(scale)
            print(f'Escala vertical canal {channel}: {v_scale:.2f} [V/div]')
            return v_scale
        except Exception as e:
            print("Error al obtener la escala vertical:", e)
            self.close()
            return None

    def set_channel_scale(self, channel: int, value: float) -> None:
        r"""Configura la escala vertical en el canal seleccionado.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a configurar (1 o 2).
            value (float): Tensión por división requerida en 
                :math:`\unit{\volt/\text{div}}`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(f':channel{channel}:scale {value}')
            v_scale = self.get_channel_scale(channel)
            if v_scale == value:
                print(f'Escala vertical CH{channel}: {v_scale:.2f} [V/div]')
            else:
                print('No se pudo configurar la escala vertical.')
        except Exception as e:
            print("Error al configurar la escala vertical:", e)
            self.close()

    def get_timebase_scale(self) -> Optional[float]:
        r"""Consulta el valor de la base de tiempo horizontal.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[float]: Escala de tiempo en 
                :math:`\unit{\second/\text{div}}`, o ``None`` en caso 
                de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        try:
            scale = self.dso.query(':timebase:scale?')
            h_scale = float(scale)
            print(f'Escala horizontal: {h_scale} [s/div]')
            return h_scale
        except Exception as e:
            print("Error al obtener la escala horizontal:", e)
            self.close()
            return None

    def set_timebase_scale(self, value: float) -> None:
        r"""Configura la base de tiempo horizontal para la digitalización.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            value (float): Tiempo por división requerido en 
                :math:`\unit{\second/\text{div}}`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(f':timebase:scale {value}')
            h_scale = self.get_timebase_scale()
            if h_scale == value:
                print(f'Escala Horizontal configurada a: {h_scale} [s/div]')
            else:
                print('No se pudo configurar la escala horizontal.')
        except Exception as e:
            print("Error al configurar la escala horizontal:", e)
            self.close()

    def get_timebase_position(self) -> Optional[float]:
        r"""Consulta la posición horizontal (delay) del punto de disparo 
        en el eje temporal.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[float]: Desplazamiento temporal en 
                :math:`\unit{\second}`, o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        try:
            position = float(self.dso.query(':timebase:delay?'))
            print(f'Posición horizontal: {position} [s]')
            return position
        except Exception as e:
            print("Error al obtener la posición horizontal:", e)
            self.close()
            return None

    def set_timebase_position(self, value: float) -> None:
        r"""Configura la posición horizontal (delay) del punto de 
        disparo en el eje temporal.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            value (float): Tiempo de retardo en :math:`\unit{\second}`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(f':timebase:delay {value}')
            position = self.get_timebase_position()
            if position == value:
                print(f'Posición horizontal configurada a: {position} [s]')
            else:
                print('No se pudo configurar la posición horizontal.')
        except Exception as e:
            print("Error al configurar la posición horizontal:", e)
            self.close()

    def get_trigger_level(self) -> Optional[float]:
        r"""Consulta el umbral absoluto de tensión utilizado para la 
        detección del flanco de disparo.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[float]: Nivel de trigger en :math:`\unit{\volt}`, 
                o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        try:
            level = float(self.dso.query(':trigger:level?'))
            return level
        except Exception as e:
            print("Error al obtener el nivel de disparo:", e)
            self.close()
            return None

    def set_trigger_level(self, trigger_level: float) -> None:
        r"""Configura el umbral absoluto de tensión de disparo.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            trigger_level (float): Tensión requerida en 
                :math:`\unit{\volt}`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(f':trigger:level {trigger_level}')
            if self.get_trigger_level() == trigger_level:
                print(f"Nivel de disparo configurado: {trigger_level}")
            else:
                print("No se pudo configurar el nivel de disparo.")
        except Exception as e:
            print("Error al configurar el nivel de disparo:", e)
            self.close()

    def get_trigger_slope(self) -> Optional[str]:
        r"""Consulta la polaridad de la pendiente (flanco) del disparo.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Dirección de pendiente detectada ('Positivo' 
                o 'Negativo'), o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        slopes = ('Positivo', 'Negativo')
        try:
            slope = self.dso.query(':trigger:slope?')
            print(f'Flanco de trigger: {slopes[int(slope)]}')
            return slopes[int(slope)]
        except Exception as e:
            print("Error al obtener el flanco de trigger:", e)
            self.close()
            return None

    def set_trigger_slope(self, slope: int) -> None:
        r"""Configura la polaridad de la pendiente (flanco) del disparo.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            slope (int): Dirección requerida: 0 para 'Positivo', 1 para 
                'Negativo'.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        slopes = ('Positivo', 'Negativo')
        try:
            self.dso.write(f':trigger:slope {slope}')
            current_slope = self.get_trigger_slope()
            if current_slope == slopes[slope]:
                print(f'Flanco de trigger configurado a: {current_slope}')
            else:
                print('No se pudo configurar el flanco de trigger.')
        except Exception as e:
            print("Error al configurar el flanco de trigger:", e)
            self.close()

    def get_trigger_state(self) -> Optional[str]:
        r"""Verifica si el osciloscopio capturó una señal.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Estado síncrono de la captura ('No disparado' 
                o 'Disparado'), o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        states = ('No disparado', 'Disparado')
        try:
            state = self.dso.query(':trigger:state?')
            print(f'Estado de trigger: {states[int(state)]}')
            return states[int(state)]
        except Exception as e:
            print("Error al obtener el estado de trigger:", e)
            self.close()
            return None

    def get_channel_display(self, channel: int) -> Optional[str]:
        r"""Consulta la visualización de un canal en pantalla.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Optional[str]: Estado de visualización ('OFF' u 'ON'), o 
                ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        states = ('OFF', 'ON')
        try:
            display = self.dso.query(f':channel{channel}:display?')
            status = states[int(display)]
            print(f'Canal {channel} está {status}')
            return status
        except Exception as e:
            print("Error al obtener el estado de visualización del canal:", e)
            self.close()
            return None

    def set_channel_display(self, channel: int, state: int) -> None:
        r"""Configura la visualización de un canal en pantalla.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a configurar (1 o 2).
            state (int): Estado de visualización: 0 para apagar ('OFF'), 
                1 para encender ('ON').
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        states = ('OFF', 'ON')
        try:
            self.dso.write(f':channel{channel}:display {state}')
            current_state = self.get_channel_display(channel)
            if current_state == states[int(state)]:
                print(f'Canal {channel} configurado a: {current_state}')
            else:
                print('No se pudo configurar la visualización del canal.')
        except Exception as e:
            print("Error al configurar la visualización del canal:", e)
            self.close()

    def get_channel_offset(self, channel: int) -> Optional[float]:
        r"""Consulta la tensión continua (offset) de compensación 
        vertical del canal indicado.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Optional[float]: Tensión continua de desplazamiento 
                inyectada en :math:`\unit{\volt}`, o ``None`` en caso 
                de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        try:
            offset = float(self.dso.query(f':channel{channel}:offset?'))
            print(f'Offset del canal {channel}: {offset} [V]')
            return offset
        except Exception as e:
            print("Error al obtener el offset del canal:", e)
            self.close()
            return None

    def set_channel_offset(self, channel: int, offset: float) -> None:
        r"""Configura la tensión continua (offset) de compensación 
        vertical del canal indicado.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a configurar (1 o 2).
            offset (float): Tensión continua de desplazamiento en 
                :math:`\unit{\volt}`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(f':channel{channel}:offset {offset}')
            current_offset = self.get_channel_offset(channel)
            if current_offset == offset:
                print(f'Offset de CH{channel}: {current_offset} [V]')
            else:
                print('No se pudo configurar el offset del canal.')
        except Exception as e:
            print("Error al configurar el offset del canal:", e)
            self.close()

    def set_single_trigger(self) -> None:
        r"""Configura el disparo del osciloscopio para capturar un único 
        evento.
        
        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(':single')
            print("Disparo único configurado exitosamente.")
        except Exception as e:
            print("Error al configurar el disparo único:", e)
            self.close()

    def close(self) -> None:
        r"""Termina y libera de manera ordenada la interfaz de conexión 
        VISA y el ResourceManager.

        Este método actúa principalmente como un mecanismo interno de 
        seguridad (failsafe) que se ejecuta automáticamente al capturar 
        excepciones de comunicación. También puede ser invocado por 
        capas superiores de la aplicación (ej. interfaces gráficas) para 
        limpiar sesiones previas o abortadas antes de intentar una 
        reconexión.
        """
        if self.dso is not None:
            try:
                self.dso.close()
                print("Conexión con el instrumento cerrada exitosamente.")
            except Exception as e:
                print("Error al cerrar la conexión con el instrumento:", e)
            finally:
                self.dso = None

        if hasattr(self, 'rm') and self.rm is not None:
            try:
                self.rm.close()
                print("Gestor de recursos cerrado exitosamente.")
            except Exception as e:
                print("Error al cerrar el gestor de recursos:", e)
            finally:
                self.rm = None

    def __del__(self) -> None:
        r"""Destructor síncrono que garantiza la liberación de 
        descriptores de hardware del SO invocando :meth:`close`.

        Asegura que los recursos se liberen cuando el objeto es 
        destruido.
        """
        self.close()

    @staticmethod
    def process_multipliers(
            value: Union[str, float], 
            unit: str
    ) -> Optional[float]:
        r"""Procesa y convierte valores numéricos con prefijos del 
        Sistema Internacional (SI) de unidades.

        Aplica factores de escala de manera agnóstica para transformar a 
        unidades base (Voltios o Segundos). Si la unidad introducida no 
        es reconocida, asume automáticamente un multiplicador base de 
        ``1.0``. Soporta de manera consistente los submúltiplos de micro 
        tanto en formato ASCII ("u") como en su codificación formal 
        UTF-8 ("µ").

        Args:
            value (Union[str, float]): Magnitud numérica escalar (texto 
                numérico o primitivo flotante).
            unit (str): Símbolo del submúltiplo físico ('V', 'mV', 'uV', 
                'µV', 's', 'ms', 'us', 'µs', 'ns').

        Returns:
            Optional[float]: Valor absoluto escalado a la unidad 
                fundamental del SI, o ``None`` si el valor ingresado es 
                inválido.
        """
        multipliers = {
            "V": 1.0,        # Volt.
            "mV": 1e-3,      # Milivolt.
            "uV": 1e-6,      # Microvolt (ASCII).
            "µV": 1e-6,      # Microvolt (SI/UTF-8).
            "s": 1.0,        # Segundo.
            "ms": 1e-3,      # Milisegundo.
            "us": 1e-6,      # Microsegundo (ASCII).
            "µs": 1e-6,      # Microsegundo (SI/UTF-8).
            "ns": 1e-9       # Nanosegundo.
        }

        try:
            numerical_value = float(value)
            factor = multipliers.get(unit, 1.0)
            scale = numerical_value * factor
            
            print(f"El parámetro final generado es: {scale}")
            return scale

        except ValueError:
            # Por si el usuario dejó el campo en blanco o no es un número.
            print("Esperando un número válido en la lista...")
            return None

# =============================================================================
# UNUSED / RESERVED METHODS
# =============================================================================
# Los siguientes métodos no se acoplan a la lógica principal actualmente,
# pero se preservan para futuras extensiones del sistema de adquisición.

    def get_setting(self) -> None:
        r"""Consulta e imprime por consola la configuración actual del 
        instrumento (``*LRN?``).

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            current_setting = self.dso.query('*LRN?')
            print(f"Configuracion actual: {current_setting}")
        except Exception as e:
            print("Error al consultar configuración:", e)
            self.close()

    def get_trigger_coupling(self) -> Optional[str]:
        r"""Consulta el acoplamiento eléctrico del circuito del trigger.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Modo de acoplamiento analógico detectado 
                ('AC' o 'DC'), o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        couplings = ('AC', 'DC')
        try:
            coupling = self.dso.query(':trigger:couple?')
            print(f'Acoplamiento de trigger: {couplings[int(coupling)]}')
            return couplings[int(coupling)]
        except Exception as e:
            print("Error al obtener el acoplamiento de trigger:", e)
            self.close()
            return None

    def set_trigger_coupling(self, coupling: int) -> None:
        r"""Configura el acoplamiento eléctrico del circuito del trigger.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            coupling (int): Índice de modo: 0 para 'AC', 1 para 'DC'.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        couplings = ('AC', 'DC')
        try:
            self.dso.write(f':trigger:couple {coupling}')
            current_coupling = self.get_trigger_coupling()
            if current_coupling == couplings[coupling]:
                print(f'Acoplamiento de trigger: {current_coupling}')
            else:
                print('No se pudo configurar el acoplamiento de trigger.')
        except Exception as e:
            print("Error al configurar el acoplamiento de trigger:", e)
            self.close()

    def get_trigger_mode(self) -> Optional[str]:
        r"""Consulta el modo de actualización del trigger.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Modo de actualización del trigger:
                * 0: 'Auto'.
                * 1: 'Normal'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        modes = ('Auto', 'Normal')
        try:
            mode = self.dso.query(':trigger:mode?')
            print(f'Modo de trigger: {modes[int(mode)-1]}')
            return modes[int(mode)-1]
        except Exception as e:
            print("Error al obtener el modo de trigger:", e)
            self.close()
            return None

    def set_trigger_mode(self, mode: int) -> None:
        r"""Configura el modo actualización del trigger.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            mode (int): Índice de selección (0: 'Auto', 1: 'Normal').
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        modes = ('Auto', 'Normal')
        try:
            self.dso.write(f':trigger:mode {mode+1}')
            current_mode = self.get_trigger_mode()
            if current_mode == modes[mode]:
                print(f'Modo de trigger configurado a: {current_mode}')
            else:
                print('No se pudo configurar el modo de trigger.')
        except Exception as e:
            print("Error al configurar el modo de trigger:", e)
            self.close()

    def get_trigger_nrej(self) -> Optional[str]:
        r"""Consulta el estado del circuito de filtro de ruido acoplado 
        al trigger.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Estado del filtro de ruido del trigger:
                * 'OFF'.
                * 'ON'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        states = ('OFF', 'ON')
        try:
            nrej = self.dso.query(':trigger:nrej?')
            status = states[int(nrej)]
            print(f'Filtro de ruido de trigger está {status}')
            return status
        except Exception as e:
            print("Error obteniendo estado de filtro de ruido de trigger:", e)
            self.close()
            return None

    def set_trigger_nrej(self, state: int) -> None:
        r"""Habilita o deshabilita el circuito de filtro de ruido 
        acoplado al trigger.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            state (int): Estado de habilitación (0: 'OFF', 1: 'ON').
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        states = ('OFF', 'ON')
        try:
            self.dso.write(f':trigger:nrej {state}')
            current_state = self.get_trigger_nrej()
            if current_state == states[int(state)]:
                print(f'Filtro de ruido de trigger: {current_state}')
            else:
                print('No se pudo configurar el filtro de ruido de trigger.')
        except Exception as e:
            print("Error al configurar el filtro de ruido de trigger:", e)
            self.close()

    def get_trigger_reject(self) -> Optional[str]:
        r"""Consulta el tipo de filtro de frecuencia acoplado al trigger.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Modo de filtrado ('OFF', 'LF', 'HF'), o 
                ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        modes = ('OFF', 'LF', 'HF')
        try:
            rej = self.dso.query(':trigger:reject?')
            print(f'Filtro de ruido de trigger: {modes[int(rej)]}')
            return modes[int(rej)]
        except Exception as e:
            print("Error al obtener el filtro de ruido de trigger:", e)
            self.close()
            return None

    def set_trigger_reject(self, mode: int) -> None:
        r"""Configura el tipo de filtro de frecuencia acoplado al trigger.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            mode (int): Tipo de filtro del trigger:
                * 0: 'OFF' (Apagado).
                * 1: 'LF' (Baja frecuencia).
                * 2: 'HF' (Alta frecuencia).
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        modes = ('OFF', 'LF', 'HF')
        try:
            self.dso.write(f':trigger:reject {mode}')
            current_mode = self.get_trigger_reject()
            if current_mode == modes[mode]:
                print(f'Filtro de ruido de trigger: {current_mode}')
            else:
                print('No se pudo configurar el filtro de ruido de trigger.')
        except Exception as e:
            print("Error al configurar el filtro de ruido de trigger:", e)
            self.close()

    def get_trigger_source(self) -> Optional[str]:
        r"""Consulta cuál es la señal de referencia acoplada al trigger.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Identificador de fuente de trigger:
                * 0: 'Canal 1'.
                * 1: 'Canal 2'.
                * 2: 'Externo'.
                * 3: 'Red'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        sources = ('Canal 1', 'Canal 2', 'Externo', 'Red')
        try:
            source = self.dso.query(':trigger:source?')
            print(f'Fuente de trigger: {sources[int(source)]}')
            return sources[int(source)]
        except Exception as e:
            print("Error al obtener la fuente de trigger:", e)
            self.close()
            return None

    def set_trigger_source(self, source: int) -> None:
        r"""Configura la señal de referencia acoplada al trigger.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            source (int): Identificador de fuente de trigger:
                * 0: 'Canal 1'.
                * 1: 'Canal 2'.
                * 2: 'Externo'.
                * 3: 'Red'.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        sources = ('Canal 1', 'Canal 2', 'Externo', 'Red')
        try:
            self.dso.write(f':trigger:source {source}')
            current_source = self.get_trigger_source()
            if current_source == sources[source]:
                print(f'Fuente de trigger configurada a: {current_source}')
            else:
                print('No se pudo configurar la fuente de trigger.')
        except Exception as e:
            print("Error al configurar la fuente de trigger:", e)
            self.close()

    def get_trigger_type(self) -> Optional[str]:
        r"""Consulta el tipo de evento disparador del osciloscopio.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Tipo de evento de trigger:
                * 0: 'Edge'.
                * 1: 'Video'.
                * 2: 'Pulse'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        types = ('Edge', 'Video', 'Pulse')
        try:
            ttype = self.dso.query(':trigger:type?')
            print(f'Tipo de trigger: {types[int(ttype)]}')
            return types[int(ttype)]
        except Exception as e:
            print("Error al obtener el tipo de trigger:", e)
            self.close()
            return None

    def set_trigger_type(self, ttype: int) -> None:
        r"""Configura el tipo de evento disparador del osciloscopio.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            ttype (int): Identificador de fuente de trigger:
                * 0: 'Edge'.
                * 1: 'Video'.
                * 2: 'Pulse'.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        types = ('Edge', 'Video', 'Pulse')
        try:
            self.dso.write(f':trigger:type {ttype}')
            current_type = self.get_trigger_type()
            if current_type == types[ttype]:
                print(f'Tipo de trigger configurado a: {current_type}')
            else:
                print('No se pudo configurar el tipo de trigger.')
        except Exception as e:
            print("Error al configurar el tipo de trigger:", e)
            self.close()

    def get_acquire_mode(self) -> Optional[str]:
        r"""Consulta el modo de adquisición del osciloscopio.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Returns:
            Optional[str]: Modo de adquisición:
                * 0: 'Normal'.
                * 1: 'Peak detect'.
                * 2: 'Average'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        modes = ('Normal', 'Peak detect', 'Average')
        try:
            mode = self.dso.query(':acquire:mode?')
            print(f'Modo de adquisición: {modes[int(mode)]}')
            return modes[int(mode)]
        except Exception as e:
            print("Error al obtener el modo de adquisición:", e)
            self.close()
            return None

    def set_acquire_mode(self, mode: int) -> None:
        r"""Configura el modo de adquisición del osciloscopio.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            mode (int): Modo de adquisición:
                * 0: 'Normal'.
                * 1: 'Peak detect'.
                * 2: 'Average'.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        modes = ('Normal', 'Peak detect', 'Average')
        try:
            self.dso.write(f':acquire:mode {mode}')
            current_mode = self.get_acquire_mode()
            if current_mode == modes[mode]:
                print(f'Modo de adquisición configurado a: {current_mode}')
            else:
                print('No se pudo configurar el modo de adquisición.')
        except Exception as e:
            print("Error al configurar el modo de adquisición:", e)
            self.close()

    def get_channel_coupling(self, channel: int) -> Optional[str]:
        r"""Consulta el tipo de acoplamiento galvánico de entrada del 
        canal de entrada.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Optional[str]: Tipo de acoplamiento de entrada:
                * 0: 'AC'.
                * 1: 'DC'.
                * 2: 'GND'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        couplings = ('AC', 'DC', 'GND')
        try:
            coupling = self.dso.query(f':channel{channel}:coupling?')
            print(f'Acoplamiento de CH{channel}: {couplings[int(coupling)]}')
            return couplings[int(coupling)]
        except Exception as e:
            print("Error al obtener el acoplamiento del canal:", e)
            self.close()
            return None

    def set_channel_coupling(self, channel: int, coupling: int) -> None:
        r"""Configura el tipo de acoplamiento galvánico de entrada del 
        canal de entrada.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a configurar (1 o 2).
            coupling (int): Tipo de acoplamiento de entrada:
                * 0: 'AC'.
                * 1: 'DC'.
                * 2: 'GND'.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        couplings = ('AC', 'DC', 'GND')
        try:
            self.dso.write(f':channel{channel}:coupling {coupling}')
            current_coupling = self.get_channel_coupling(channel)
            if current_coupling == couplings[coupling]:
                print(f'Acoplamiento de CH{channel}: {current_coupling}')
            else:
                print('No se pudo configurar el acoplamiento del canal.')
        except Exception as e:
            print("Error al configurar el acoplamiento del canal:", e)
            self.close()

    def get_channel_type(self, channel: int) -> Optional[str]:
        r"""Consulta la magnitud física asociada lógicamente a la punta 
        de prueba del canal.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Optional[str]: Magnitud física del canal:
                * 0: 'Tensión'.
                * 1: 'Corriente'.
                * ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        types = ('Tensión', 'Corriente')
        try:
            ctype = self.dso.query(f':channel{channel}:probe:type?')
            print(f'Tipo de prueba del canal {channel}: {types[int(ctype)]}')
            return types[int(ctype)]
        except Exception as e:
            print("Error al obtener el tipo de prueba del canal:", e)
            self.close()
            return None

    def set_channel_type(self, channel: int, ctype: int) -> None:
        r"""Configura la magnitud física asociada lógicamente a la punta 
        de prueba del canal.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a configurar (1 o 2).
            ctype (int): Magnitud física del canal:
                * 0: 'Tensión' (:math:`\unit{\volt}`).
                * 1: 'Corriente' (:math:`\unit{\ampere}`).
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        types = ('Tensión', 'Corriente')
        try:
            self.dso.write(f':channel{channel}:probe:type {ctype}')
            current_type = self.get_channel_type(channel)
            if current_type == types[ctype]:
                print(f'Magnitud del CH{channel}: {current_type}')
            else:
                print('No se pudo configurar el tipo de prueba del canal.')
        except Exception as e:
            print("Error al configurar el tipo de prueba del canal:", e)
            self.close()

    def get_channel_attenuation(self, channel: int) -> Optional[float]:
        r"""Consulta el multiplicador de escala interno (Probe Ratio) de 
        la punta del canal.

        En caso de error de lectura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a consultar (1 o 2).

        Returns:
            Optional[float]: Factor de atenuación de la punta. Valores 
                posibles: {0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 
                500, 1000, 2000}, o ``None`` en caso de error.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return None

        try:
            cmd = f':channel{channel}:probe:ratio?'
            attenuation = float(self.dso.query(cmd))
            print(f'Factor de atenuación del canal {channel}: {attenuation}')
            return attenuation
        except Exception as e:
            print("Error al obtener el factor de atenuación del canal:", e)
            self.close()
            return None

    def set_channel_attenuation(
            self,
            channel: int,
            attenuation: float
    ) -> None:
        r"""Configura el multiplicador de escala interno (Probe Ratio) 
        de la punta del canal.

        En caso de error de escritura, captura la excepción y ejecuta 
        :meth:`close`.

        Args:
            channel (int): Canal a configurar (1 o 2).
            attenuation (float): Factor de atenuación de la punta. 
                Valores posibles: {0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 
                100, 200, 500, 1000, 2000}.
        """
        if self.dso is None:
            print("Error: El instrumento no está conectado.")
            return

        try:
            self.dso.write(f':channel{channel}:probe:ratio {attenuation}')
            current_attenuation = self.get_channel_attenuation(channel)
            if current_attenuation == attenuation:
                print(f'Atenuación del CH{channel}: {current_attenuation}')
            else:
                print('No se pudo configurar el factor de atenuación del canal.')
        except Exception as e:
            print("Error al configurar el factor de atenuación del canal:", e)
            self.close()