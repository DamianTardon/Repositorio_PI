from pathlib import Path
from datetime import datetime
import pandas as pd
import h5py
import numpy as np
import struct

class FileManager:
    def __init__(self, project_name="Nro_Item"):
        # 1. Definir Rutas
        self.base = Path.cwd() / project_name
        self.raw = self.base / "01 Respaldo"
        self.analysis = self.base / "02 Analisis de datos"
        self.results = self.base / "03 Resultados"
        
        # 2. Crear Estructura Automáticamente al iniciar
        #self._create_structure()
    
    def _create_structure(self):
        """Crea las carpetas si no existen"""
        for carpeta in [self.raw, self.analysis, self.results]:
            carpeta.mkdir(parents=True, exist_ok=True)
            #print(f"Verificado: {carpeta}")

    def get_new_name(self, prefijo="medicion", extension=".bin"):
        """Genera una ruta con timestamp para no sobrescribir nunca"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"{prefijo}_{timestamp}{extension}"
        
        if extension == ".bin":
            return self.raw / nombre
        elif extension == ".h5":
            return self.analysis / nombre
        elif extension == ".png" or extension == ".pdf":
            return self.results / nombre
        else:
            return self.base / nombre
        
    # Crear BIN (int16): para guardar datos originales como copia de seguridad.
    @staticmethod
    def create_bin_int16(data, file_path):
        with open(file_path, "wb") as f:
            f.write(data)
            #print(f"Se creó '{file_path}'")

    # Crear HDF5: para almacenamiento principal y procesamiento.
    @staticmethod
    def create_hdf5(time, ch1, file_path):
        # Guarda donde tú le digas
        with h5py.File(file_path, "w") as f:
            f.create_dataset("Tiempo [s]", data=time, compression="gzip")
            f.create_dataset("Tensión [V]", data=ch1, compression="gzip")
        #print(f"Se creó '{file_path}'")

    # Crear CSV: para exportar datos.
    @staticmethod
    def create_csv(time, tension, file_path):
        # Crear el DataFrame con Nombres de Columnas.
        df = pd.DataFrame({
            "Tiempo [s]": time,
            "Tensión [V]": tension
        })
        # float_format='%.4E' guarda en notación científica (ej: 1.2345E-03).
        df.to_csv(file_path, index=False, sep=',', float_format='%.4E')
        print(f"Se creó '{file_path}'")

    @staticmethod
    def read_bin_without_header(file_path):
        # dtype='>i2': Big Endian (>), 2 bytes int (i2)
        raw_data = np.fromfile(file_path, dtype='>i2')
        waveform = raw_data / 25.0
        return waveform

    @staticmethod
    def read_bin_with_header(file_path):
        with open(file_path, "rb") as f:
            # Leer primeros 2 bytes (# + Digito)
            header_start = f.read(2)
            
            # Parsear el dígito de tamaño
            data_size_digit = int(chr(header_start[1]))
            
            # Leer el tamaño del bloque (los siguientes N bytes)
            size_bytes = f.read(data_size_digit)
            data_size = int(size_bytes.decode('ascii'))
            
            print("Cabecera: " + header_start.decode('ascii') + size_bytes.decode('ascii'))
            print(f"Datos a leer: {data_size} bytes")

            time_interval = f.read(8)
            # >  : Big Endian
            # f  : Float (4 bytes) -> Periodo de muestreo
            # 4x : Padding (4 bytes) -> Ignorar bloque de datos sin uso
            dt = struct.unpack('>f4x', time_interval)[0]
            
            print(f"Periodo de muestreo (dt): {dt:.2e} [s] = {dt*1e9:.0f} [ns]")
            
            # Leemos el resto del archivo (que debe coincidir con data_size)
            raw_bytes = f.read()
            
            # Validación de seguridad (opcional pero recomendada)
            if len(raw_bytes) != data_size-8:
                print(f"Advertencia: Se esperaban {data_size} bytes pero se leyeron {len(raw_bytes)}")

            raw_data = np.frombuffer(raw_bytes, dtype='>i2')
            waveform = raw_data / 25.0
            
        return waveform, dt
    
    @staticmethod
    def read_csv(file_path):
        # 'usecols' leer SOLAMENTE esa columna.
        df = pd.read_csv(file_path, usecols=["Tensión [V]"])
        
        # df[titulo_columna] accede a los datos
        # .values lo convierte a un array de NumPy
        return df["Tensión [V]"].values
    
    @staticmethod
    def read_h5(file_path):
        with h5py.File(file_path, "r") as f:
            return f["Tensión [V]"][:]
        
    @staticmethod
    def read_calibration_file(file_path):
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

            for line in f:
                if line.strip():
                    data.append(float(line.strip()))

        return metadata, data