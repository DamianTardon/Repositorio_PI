from pathlib import Path
from datetime import datetime
import pandas as pd
import h5py
import numpy as np
import struct
import os

class FileManager:
    # Constante de cuantización vertical del ADC específica del modelo GWInstekGDS1000AU.
    ADC_STEPS_PER_DIV = 25.0

    def __init__(self, project_name="item-año - cliente"):
        # Definir Rutas desde donde se ejecuta el programa.
        self.base = Path.cwd() / project_name
        self.raw = self.base / "01 Respaldo"
        self.analysis = self.base / "02 Analisis de datos"
        self.results = self.base / "03 Resultados"

    def create_new_structure(self, project_name, base_dir=None):
        # Si se recibe una ruta base, se usa. Si no, usa el directorio de trabajo (cwd).
        if base_dir:
            self.base = Path(base_dir) / project_name
        else:
            self.base = Path.cwd() / project_name

        self.raw = self.base / "01 Respaldo"
        self.analysis = self.base / "02 Analisis de datos"
        self.results = self.base / "03 Resultados"
        self._create_structure()

    def _create_structure(self):
        # Crea la carpeta si no existe. Y si ya existe no hace nada.
        for carpeta in [self.raw, self.analysis, self.results]:
            carpeta.mkdir(parents=True, exist_ok=True)

    def get_new_filename(self, filename, extension):
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
    def create_csv(data, file_path):
        # Crear CSV: para guardar una copia de seguridad datos originales de la onda.
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

    @staticmethod
    def read_bin_without_header(file_path):
        # dtype='>i2': Big Endian (>), 2 bytes int (i2).
        raw_data = np.fromfile(file_path, dtype='>i2')
        waveform = raw_data / FileManager.ADC_STEPS_PER_DIV
        return waveform

    @staticmethod
    def read_bin_with_header(file_path):
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
    def read_h5(file_path):
        with h5py.File(file_path, "r") as f:
            return f["Tensión [V]"][:]

    @staticmethod
    def read_TDG_file(file_path):
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

    def get_existing_wave_count(self, h5_file_path):
        # Leer el archivo HDF5 del ensayo y devolver la cantidad de ondas guardadas.
        if not os.path.exists(h5_file_path):
            return 0, 0

        # Contar la cantidad de ondas registradas.
        with h5py.File(h5_file_path, 'r') as f:
            waves = [k for k in f.keys() if k.startswith("Onda")]
            refs = [k for k in f.keys() if k.startswith("Referencia")]
            return len(waves), len(refs)

    @staticmethod
    def _save_dataset(group, name, data):
        if data is not None:
            if name in group:
                del group[name]
            group.create_dataset(name, data=data, compression="gzip", compression_opts=4)

    def append_to_hdf5(self, file_path, wave_name, global_data, wave_data, time_data, ch1_data, ch2_data=None):
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

    def read_hdf5_waveforms(self, file_path):
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

    def export_hdf5_results_to_dataframe(self, file_path):
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