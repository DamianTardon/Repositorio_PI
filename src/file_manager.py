"""Módulo de almacenamiento y administración persistente del sistema de ficheros del ensayo.

Rige las rutinas de creación de directorios del proyecto, guardado de respaldos originales
en texto plano (CSV) y persistencia indexada jerárquica masiva de matrices analíticas mediante HDF5.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import pandas as pd
import h5py
import numpy as np
import struct
import os

from typing import Union, Tuple, Optional, Any, Dict, List

class FileManager:
    """Administra las llamadas lógicas de lectura/escritura (IO) y la integridad de bases binarias estructuradas.

    Maneja el ruteo dinámico del proyecto, la exportación de resultados a formatos 
    planos (CSV, Excel) y la escritura/lectura estructurada de matrices de onda y 
    metadatos mediante una base de datos jerárquica HDF5.

    Attributes:
        ADC_STEPS_PER_DIV (float): Constante de cuantización vertical del conversor ADC, 
            específica de la serie GW Instek GDS-1000A-U (:math:`\num{25.0}` pasos por división).
        base (Path): Ruta absoluta al directorio raíz del proyecto de ensayo actual.
        raw (Path): Subdirectorio asignado a las copias de seguridad de datos crudos ('01 Respaldo').
        analysis (Path): Subdirectorio donde se confina la base estructurada indexada HDF5 ('02 Analisis de datos').
        results (Path): Ubicación física asignada para reportes y archivos exportados ('03 Resultados').
    """

    #: Constante de cuantización vertical del ADC de la serie GW Instek GDS 1000AU.
    ADC_STEPS_PER_DIV: float = 25.0

    def __init__(self, project_name: str = "item-año - cliente") -> None:
        """Inicializa los apuntadores de ruta predeterminados asumiendo el directorio de trabajo (cwd).

        Args:
            project_name (str, optional): Nombre estandarizado para la carpeta raíz 
                del proyecto. Por defecto es "item-año - cliente".
        """

        # Definir Rutas desde donde se ejecuta el programa.
        self.base = Path.cwd() / project_name
        self.raw = self.base / "01 Respaldo"
        self.analysis = self.base / "02 Analisis de datos"
        self.results = self.base / "03 Resultados"

    def create_new_structure(self, project_name: str, base_dir: Optional[Union[str, Path]] = None) -> None:
        """Sobrescribe el entorno de directorios y detona su creación física en disco.

        Args:
            project_name (str): Nombre del directorio raíz del ensayo.
            base_dir (Optional[Union[str, Path]], optional): Ruta base alternativa de creación. 
                Si es ``None``, utiliza el directorio de trabajo actual (`Path.cwd()`).
        """
        # Si se recibe una ruta base, se usa. Si no, usa el directorio de trabajo (cwd).
        if base_dir:
            self.base = Path(base_dir) / project_name
        else:
            self.base = Path.cwd() / project_name

        self.raw = self.base / "01 Respaldo"
        self.analysis = self.base / "02 Analisis de datos"
        self.results = self.base / "03 Resultados"
        self._create_structure()

    def _create_structure(self) -> None:
        """Garantiza la creación física en disco de los nodos de directorios del mapa Path si no existen."""
        # Crea la carpeta si no existe. Y si ya existe no hace nada.
        for carpeta in [self.raw, self.analysis, self.results]:
            carpeta.mkdir(parents=True, exist_ok=True)

    def get_new_filename(self, filename: str, extension: str) -> Path:
        """Construye una ruta absoluta asignando el archivo a la subcarpeta correcta según su formato.

        Asegura que el nombre contenga la extensión solicitada (añadiéndola 
        automáticamente si el usuario la omitió) y rutea el fichero dinámicamente:
            - ``.csv``: Se rutea a la carpeta de copias crudas (``self.raw``).
            - ``.h5``: Se rutea a la carpeta de bases de datos (``self.analysis``).
            - ``.png``, ``.pdf``: Se rutean a la carpeta de informes visuales (``self.results``).
            - **Fallback**: Cualquier otra extensión o ausencia de la misma se rutea al 
              directorio raíz del ensayo (``self.base``).

        Args:
            filename (str): Nombre base deseado para el archivo.
            extension (str): Sufijo normalizado de extensión (ej. '.csv').

        Returns:
            Path: Ruta unificada final apuntando al subdirectorio correspondiente.
        """
        # Asegura que el nombre termine con la extensión solicitada.
        if not filename.endswith(extension):
            filename = f"{filename}{extension}"

        if extension == ".csv":
            return self.raw / filename
        elif extension == ".h5":
            return self.analysis / filename
        elif extension in [".png", ".pdf"]:
            return self.results / filename
        else:
            return self.base / filename

    @staticmethod
    def create_csv(data: Union[dict, list, np.ndarray], file_path: Union[str, Path]) -> None:
        """Exporta copias planas de seguridad de los arreglos discretos analógicos en disco.

        Args:
            data (Union[dict, list, np.ndarray]): Arreglo de amplitudes crudas de tensiones o corrientes.
            file_path (Union[str, Path]): Ruta absoluta de destino para el archivo CSV.
        """
        # Crear CSV: para guardar una copia de seguridad datos originales de la onda.
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

    @staticmethod
    def read_bin_without_header(file_path: Union[str, Path]) -> np.ndarray:
        """Decodifica archivos binarios crudos sin cabeceras interpretando tramas Big-Endian de 16-bits.

        Args:
            file_path (Union[str, Path]): Ruta absoluta al binario.

        Returns:
            np.ndarray: Vector analógico de amplitudes escalado por :attr:`ADC_STEPS_PER_DIV`.
            
        Raises:
            FileNotFoundError: Si la ruta especificada no existe en el disco.
        """
        # dtype='>i2': Big Endian (>), 2 bytes int (i2).
        raw_data = np.fromfile(file_path, dtype='>i2')
        waveform = raw_data / FileManager.ADC_STEPS_PER_DIV
        return waveform

    @staticmethod
    def read_bin_with_header(file_path: Union[str, Path]) -> Tuple[np.ndarray, float]:
        """Parsea un archivo binario con encabezado IEEE dinámico y extrae el vector escalado y su :math:`dt`.

        Interpreta la trama inicial SCPI para determinar la longitud declarada de los datos y desempaqueta 
        el periodo de muestreo almacenado como IEEE 754 Float (Big Endian). 

        .. note::
            Implementa una validación de integridad: advierte por consola si el tamaño real 
            de los bytes leídos del buffer no coincide con lo indicado en el encabezado.
            Los datos son convertidos a tensión dividiendo por la constante de clase 
            :math:`\num{25.0}` (:attr:`ADC_STEPS_PER_DIV`).

        Args:
            file_path (Union[str, Path]): Destino absoluto del fichero binario propietario.

        Returns:
            Tuple[np.ndarray, float]: Vector escalado de la forma de onda, y periodo de muestreo 
            :math:`dt` en segundos (:math:`\qty{}{\second}`).

        Raises:
            FileNotFoundError: Si el binario no es encontrado en la ruta especificada.
            ValueError: Si la cabecera ASCII no puede ser decodificada como entero.
            struct.error: Si falla el desempaquetado de los bytes de periodo de muestreo.
        """
        with open(file_path, "rb") as f:
            # Leer primeros 2 bytes (# + Digito).
            header_start = f.read(2)

            # Parsear el dígito de tamaño.
            data_size_digit = int(chr(header_start[1]))

            # Leer el tamaño del bloque (los siguientes N bytes).
            size_bytes = f.read(data_size_digit)
            data_size = int(size_bytes.decode('ascii'))

            print("Cabecera: " + header_start.decode('ascii') + size_bytes.decode('ascii'))
            print(f"Datos a leer: {data_size} bytes")

            time_interval = f.read(8)
            # >  : Big Endian.
            # f  : Float (4 bytes) -> Periodo de muestreo.
            # 4x : Padding (4 bytes) -> Ignorar bloque de datos sin uso.
            dt = struct.unpack('>f4x', time_interval)[0]

            print(f"Periodo de muestreo (dt): {dt:.2e} [s] = {dt*1e9:.0f} [ns]")

            # Leemos el resto del archivo (que debe coincidir con data_size).
            raw_bytes = f.read()

            # Validación de seguridad.
            # Si el tamaño de los datos leídos no coincide con lo esperado, se muestra una advertencia.
            if len(raw_bytes) != data_size-8:
                print(f"Advertencia: Se esperaban {data_size} bytes pero se leyeron {len(raw_bytes)}")

            raw_data = np.frombuffer(raw_bytes, dtype='>i2')
            waveform = raw_data / ADC_STEPS_PER_DIV

        return waveform, dt

    @staticmethod
    def read_h5(file_path: Union[str, Path]) -> np.ndarray:
        """Apertura estática de conveniencia para extraer un dataset simple 'Tensión [V]' de un HDF5.

        Args:
            file_path (Union[str, Path]): Dirección física al archivo HDF5.

        Returns:
            np.ndarray: Vector de tensión recuperado.

        Raises:
            FileNotFoundError: Si no se ubica la base de datos HDF5.
            KeyError: Si el dataset clave ``"Tensión [V]"`` no existe dentro de la raíz del archivo.
        """
        with h5py.File(file_path, "r") as f:
            return f["Tensión [V]"][:]

    @staticmethod
    def read_TDG_file(file_path: Union[str, Path]) -> Tuple[Dict[str, Any], List[float]]:
        """Abre y parsea archivos de calibración del Test Data Generator (TDG).

        Args:
            file_path (Union[str, Path]): Ruta absoluta al archivo plano de la IEC.

        Returns:
            Tuple[Dict[str, Any], List[float]]: Diccionario con metadatos del archivo y lista de valores de onda.

        Raises:
            FileNotFoundError: Si el archivo TDG especificado no existe.
            ValueError: Si falla la conversión de las líneas del archivo a coma flotante.
        """
        metadata = {}
        data = []

        with open(file_path, 'r') as f:

            metadata['software_version'] = f.readline().strip()
            metadata['version_file'] = f.readline().strip()
            metadata['wave_name'] = f.readline().strip()

            line_4 = f.readline().strip()
            resolution_samples_time = line_4.split(',')

            metadata['resolution'] = resolution_samples_time[0].strip()

            samples_time = resolution_samples_time[1].strip().split(' samples at ')
            metadata['samples'] = int(samples_time[0])
            metadata['interval'] = samples_time[1].strip()

            metadata['sampling_period'] = float(f.readline().strip())

            rate_calc = 1 / metadata['sampling_period'] / 1e6 # MSa/s.
            metadata['rate'] = f"{rate_calc:.0f} MSa/s"

            for line in f:
                if line.strip():
                    data.append(float(line.strip()))

        return metadata, data

    def get_existing_wave_count(self, h5_file_path: Union[str, Path]) -> Tuple[int, int]:
        """Contabiliza los registros existentes en la base de datos jerárquica del ensayo.

        Maneja internamente la ausencia del archivo, retornando valores neutros sin interrumpir
        el flujo de la aplicación.

        Args:
            h5_file_path (Union[str, Path]): Destino físico al fichero HDF5.

        Returns:
            Tuple[int, int]: Tupla indicando la cantidad de (ondas de ensayo, ondas de referencia) 
            guardadas. Si el archivo no existe, retorna ``(0, 0)``.
        """
        # Leer el archivo HDF5 del ensayo y devolver la cantidad de ondas guardadas.
        if not os.path.exists(h5_file_path):
            return 0, 0

        # Contar la cantidad de ondas registradas.
        with h5py.File(h5_file_path, 'r') as f:
            waves = [k for k in f.keys() if k.startswith("Onda")]
            refs = [k for k in f.keys() if k.startswith("Referencia")]
            return len(waves), len(refs)

    @staticmethod
    def _save_dataset(group: h5py.Group, name: str, data: Any) -> None:
        """Inserta o sobrescribe un array como dataset comprimido GZIP en un nodo HDF5.

        Aplica compresión con un factor de 4 (``compression_opts=4``), el cual proporciona 
        un balance arquitectónico óptimo entre reducción de espacio en disco y mínima 
        latencia/consumo de CPU durante el registro masivo.

        Args:
            group (h5py.Group): Nodo o Grupo HDF5 padre.
            name (str): Clave/nombre asignado al dataset.
            data (Any): Array matemático a persistir. Si es ``None``, la operación se ignora.
        """
        if data is not None:
            if name in group:
                del group[name]
            group.create_dataset(name, data=data, compression="gzip", compression_opts=4)

    def append_to_hdf5(self, file_path: Union[str, Path], wave_name: str, global_data: Dict[str, Any], 
                       wave_data: Dict[str, Any], time_data: Dict[str, Any], 
                       ch1_data: Dict[str, Any], ch2_data: Optional[Dict[str, Any]] = None) -> None:
        """Construye y serializa el árbol jerárquico de la onda dentro del archivo HDF5 del ensayo.

        Almacena metadatos a nivel root (globales) y a nivel de grupo de onda. Particiona los vectores
        matemáticos en subgrupos ``Time``, ``CH1_Voltage`` y opcionalmente ``CH2_Current``.

        Args:
            file_path (Union[str, Path]): Ruta de la base de datos del ensayo.
            wave_name (str): Identificador único cronológico para el nodo principal (ej. 'Onda_01').
            global_data (Dict[str, Any]): Atributos transversales del ensayo (Cliente, Divisores).
            wave_data (Dict[str, Any]): Parámetros calculados para el evento (Fecha, Condiciones atmosféricas, Parámetros de la onda).
            time_data (Dict[str, Any]): Vectores de tiempo crudo y alineado.
            ch1_data (Dict[str, Any]): Matrices de amplitudes de tensión calculadas (raw, test, norm).
            ch2_data (Optional[Dict[str, Any]], optional): Matrices de corriente capturadas en CH2 (si existiesen).
        """
        # Guardar los datos de la onda con la estructura jerárquica: /Time, /CH1_Voltage, /CH2_Current.
        with h5py.File(file_path, 'a') as f:

            # Atributos globales.
            for key, value in global_data.items():
                f.attrs[key] = value

            # Grupo principal de la onda.
            # Retornar el grupo o crealo si no existe.
            grp_waveform = f.require_group(wave_name)

            # wave_data tiene los atributos: Fecha, Condiciones atmosféricas, Parámetros de la onda.
            for key, value in wave_data.items():
                grp_waveform.attrs[key] = np.nan if value is None else value

            # Grupo Tiempo.
            grp_time = grp_waveform.require_group("Time")
            self._save_dataset(grp_time, "raw_time", time_data.get("raw"))
            self._save_dataset(grp_time, "aligned_time", time_data.get("aligned"))

            # Grupo CH1 - Tension.
            grp_ch1 = grp_waveform.require_group("CH1_Voltage")
            self._save_dataset(grp_ch1, "raw_voltage", ch1_data.get("raw"))
            self._save_dataset(grp_ch1, "test_voltage", ch1_data.get("test"))
            self._save_dataset(grp_ch1, "norm_voltage", ch1_data.get("norm"))

            # Grupo CH2 - Corriente (Opcional).
            if ch2_data is not None:
                grp_ch2 = grp_waveform.require_group("CH2_Current")
                self._save_dataset(grp_ch2, "raw_current", ch2_data.get("raw"))
                self._save_dataset(grp_ch2, "test_current", ch2_data.get("test"))
                self._save_dataset(grp_ch2, "norm_current", ch2_data.get("norm"))

    def read_hdf5_waveforms(self, file_path: Union[str, Path]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """Extrae el volumen completo de la base de datos para reinyección en memoria o visualización gráfica.

        Filtra y ordena cronológicamente los nodos de tipo 'Onda_*' y 'Referencia_*'. Maneja el fallback 
        de los vectores (ej. usando array crudo si el array de test analizado no existe).

        Args:
            file_path (Union[str, Path]): Ruta del archivo de datos estructurado.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]: 
                - Diccionario con atributos globales del ensayo.
                - Diccionario anidado mapeando nombres de onda con sus respectivos vectores de tiempo, 
                  tensión y corriente. 
                *Nota:* Si el archivo en disco no existe, retorna tuplas de diccionarios vacíos ``({}, {})``.
        """
        # Leer el archivo HDF5 para recuperar los datos guardados.
        global_attrs = {}
        waves_data = {}

        if not os.path.exists(file_path):
            return global_attrs, waves_data

        with h5py.File(file_path, 'r') as f:
            # Extraer atributos globales (Cliente, Divisores, etc.).
            for key, val in f.attrs.items():
                global_attrs[key] = val.decode('utf-8') if isinstance(val, bytes) else val

            # Identificar y ordenar las ondas cronológicamente.
            wave_keys = sorted([k for k in f.keys() if k.startswith("Referencia") or k.startswith("Onda")])

            # Extraer arrays de tiempo y tensión/corriente.
            for w_name in wave_keys:
                grp = f[w_name]

                # Extraer tiempos.
                grp_time = grp.get("Time")
                if grp_time is None: continue

                t_raw = grp_time["raw_time"][:] if "raw_time" in grp_time else None
                t_aligned = grp_time["aligned_time"][:] if "aligned_time" in grp_time else None
                t_plot = t_aligned if t_aligned is not None else t_raw

                # Extraer tensiones del Canal 1.
                grp_ch1 = grp.get("CH1_Voltage")
                if grp_ch1 is None: continue

                ch1_raw = grp_ch1["raw_voltage"][:] if "raw_voltage" in grp_ch1 else None
                ch1_test = grp_ch1["test_voltage"][:] if "test_voltage" in grp_ch1 else None
                ch1_norm = grp_ch1["norm_voltage"][:] if "norm_voltage" in grp_ch1 else None
                ch1_real = ch1_test if ch1_test is not None else ch1_raw

                # Extraer corrientes del Canal 2 (Opcional).
                grp_ch2 = grp.get("CH2_Current")
                ch2_real = None
                ch2_norm = None
                if grp_ch2 is not None:
                    ch2_raw = grp_ch2["raw_current"][:] if "raw_current" in grp_ch2 else None
                    ch2_test = grp_ch2["test_current"][:] if "test_current" in grp_ch2 else None
                    ch2_norm = grp_ch2["norm_current"][:] if "norm_current" in grp_ch2 else None
                    ch2_real = ch2_test if ch2_test is not None else ch2_raw

                if t_plot is not None and ch1_real is not None:
                    waves_data[w_name] = {
                        "t": t_plot,
                        "ch1_real": ch1_real,
                        "ch1_norm": ch1_norm,
                        "ch2_real": ch2_real,
                        "ch2_norm": ch2_norm
                    }

        return global_attrs, waves_data

    def export_hdf5_results_to_dataframe(self, file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Recopila la tabla paramétrica y ambiental de las ondas de ensayo en formato tabular.

        Parsea los atributos HDF5 de las curvas de ensayo y ejecuta conversiones
        y redondeos de unidades del SI. Discrimina selectivamente la información, tomando solo 
        las 'Ondas de ensayo' y excluyendo intencionalmente las 'Ondas de Referencia'.

        Args:
            file_path (Union[str, Path]): Ruta al archivo HDF5 a consolidar.

        Returns:
            Optional[pd.DataFrame]: Estructura DataFrame limpia lista para exportación. 
            Contiene múltiples flujos de contingencia evaluados por el Presentador gráfico:
                - Retorna ``None`` si la base de datos no existe físicamente en el disco.
                - Retorna un ``pd.DataFrame`` vacío si la base existe pero carece de 
                  ondas de ensayo exportables (condición que activa una notificación UI de "Sin datos").
        """
        # Verificar si existe el archivo que contiene la información de las ondas.
        if not os.path.exists(file_path):
            return None

        data_list = []
        with h5py.File(file_path, 'r') as f:
            # Extraer el ítem global.
            item_name = f.attrs.get("Item", "Desconocido")

            # Filtrar las Referencias y tomar solo las ondas de ensayo.
            wave_keys = sorted([k for k in f.keys() if k.startswith("Onda")])

            for wave_name in wave_keys:
                grp = f[wave_name]

                # Polaridad.
                polarity = grp.attrs.get("Polarity", "N/A")
                if pd.isna(polarity):
                    polarity = "N/A"

                # Escalado de unidades.
                peak_voltage_v = grp.attrs.get("Peak_Voltage", np.nan)
                peak_voltage_kv = round(peak_voltage_v / 1e3 , 2) if not pd.isna(peak_voltage_v) else np.nan

                t1_s = grp.attrs.get("T1", np.nan)
                t1_us = round(t1_s * 1e6, 2) if not pd.isna(t1_s) else np.nan

                t2_s = grp.attrs.get("T2", np.nan)
                t2_us = round(t2_s * 1e6, 2) if not pd.isna(t2_s) else np.nan

                overshoot_val = grp.attrs.get("Overshoot", np.nan)
                overshoot = round(overshoot_val, 2) if not pd.isna(overshoot_val) else np.nan

                # Condiciones ambientales.
                t_db = grp.attrs.get("T_DB", np.nan)
                t_wb = grp.attrs.get("T_WB", np.nan)
                rh = grp.attrs.get("RH", np.nan)
                ah = grp.attrs.get("AH", np.nan)
                press = grp.attrs.get("Pressure", np.nan)

                # Construir la fila.
                data_list.append({
                    "Item": item_name,
                    "Nombre de onda": wave_name,
                    "Polaridad": polarity,
                    "Valor Pico [kV]": peak_voltage_kv,
                    "T1 [µs]": t1_us,
                    "T2 [µs]": t2_us,
                    "Sobrepasamiento [%]": overshoot,
                    "Temp. Seca [°C]": t_db,
                    "Temp. Humeda [°C]": t_wb,
                    "Humedad Rel. [%]": rh,
                    "Humedad Abs. [g/m3]": ah,
                    "Presion [hPa]": press
                })

        if not data_list:
            return pd.DataFrame()

        return pd.DataFrame(data_list)