import time
from struct import unpack
import sys
import pyvisa
import matplotlib.pyplot as plt
import numpy as np

def init_system():
    rm = pyvisa.ResourceManager()
    instrument_list = rm.list_resources()
    print("Instrumentos encontrados:", instrument_list)
    return rm

def init_instrument(manager, resource_name):
    try:
        dso = manager.open_resource(resource_name)
        dso.read_termination = '\n'
        dso.write_termination = '\n'
        idn = dso.query('*IDN?')
        print("Instrumento conectado satisfactoriamente:", idn)
    except Exception as e:
        print("Error al iniciar con el instrumento:", e)
        close_system()
    return dso

def get_block_data(instrument, channel):
    dso = instrument[1]
    try:
        v_div = get_channel_scale(instrument, channel)
        dso.write(f':acquire{channel}:state?')
        state = dso.read()
        if(state[0] == '1'):
            time.sleep(0.1)
            dso.write(f":acquire{channel}:memory?")
            inBuffer = dso.read_bytes(10)
            length = len(inBuffer)
            headerlen = 2 + int(chr(inBuffer[1]))
            pkg_length = int(inBuffer[2:headerlen]) + headerlen
            pkg_length = pkg_length - length
            
            while True:
                if(pkg_length==0):
                    break
                else:
                    if(pkg_length > 100000):
                        length = 100000
                    else:
                        length = pkg_length
                    try:
                        buf = dso.read_bytes(length)
                    except:
                        print('Error al recibir datos del instrumento!')
                        close_system(instrument)
                        sys.exit(0)
                    
                    num = len(buf)
                    inBuffer += buf
                    pkg_length = pkg_length - num
            waveform, dt = unpack_waveform(inBuffer, headerlen, v_div)
            return waveform, dt
        else:
            print('Error: Forma de onda aún no está lista.')
    except Exception as e:
        print("Error al obtener datos:", e)
        close_system(instrument)
        return None, None

def unpack_waveform(inBuffer, headerlen, vdiv):
    print(inBuffer[:headerlen])
    dt = unpack('>f', inBuffer[headerlen : headerlen + 4])[0]
    #print(f'Periodo de muestreo = {dt} [s]')
    print(f'Periodo de muestreo = {dt*1e9:.0f} [ns]')
    waveform_raw = unpack('>%sh' % (int(len(inBuffer[headerlen + 8:]) / 2)), inBuffer[headerlen + 8:])
    waveform_raw = np.array(waveform_raw)
    num = len(waveform_raw)
    print(f'Cantidad de muestras = {num}')
    waveform = waveform_raw * vdiv / 25.0
    return waveform, dt

def default_settings(instrument):
    dso = instrument[1]
    try:
        dso.write('*RST')
        print("Se restableció el instrumento a la configuración de fábrica exitosamente.")
    except Exception as e:
        print("Error al restablecer el instrumento:", e)
        close_system(instrument)

def get_setting(instrument):
    dso = instrument[1]
    try:
        current_setting = dso.query('*LRN?')
        print(f"Configuracion actual: {current_setting}")
    except Exception as e:
        print("Error al consultar configuración:", e)
        close_system(instrument)

def get_channel_scale(instrument, channel):
    dso = instrument[1]
    try:
        scale = dso.query(f':channel{channel}:scale?')
        v_scale = float(scale)
        print(f'Escala vertical: {v_scale:.2f} [V/div]')
        return v_scale
    except Exception as e:
        print("Error al obtener la escala vertical:", e)
        close_system(instrument)

def set_channel_scale(instrument, channel, value):
    dso = instrument[1]
    try:
        dso.write(f':channel{channel}:scale {value}')
        v_scale = get_channel_scale(instrument, channel)
        if v_scale == value:
            print(f'Escala vertical configurada a: {v_scale:.2f} [V/div]')
        else:
            print('No se pudo configurar la escala vertical.')
    except Exception as e:
        print("Error al obtener la escala vertical:", e)
        close_system(instrument)

def get_timebase_scale(instrument):
    dso = instrument[1]
    try:
        scale = dso.query(':timebase:scale?')
        h_scale = float(scale)
        print(f'Escala horizontal: {h_scale} [s/div]')
        return h_scale
    except Exception as e:
        print("Error al obtener la escala horizontal:", e)
        close_system(instrument)

def set_timebase_scale(instrument, value):
    dso = instrument[1]
    try:
        dso.write(f':timebase:scale {value}')
        h_scale = get_timebase_scale(instrument)
        if h_scale == value:
            print(f'Escala Horizontal configurada a: {h_scale} [s/div]')
        else:
            print('No se pudo configurar la escala horizontal.')
    except Exception as e:
        print("Error al obtener la escala horizontal:", e)
        close_system(instrument)

def get_timebase_position(instrument):
    dso = instrument[1]
    try:
        position = float(dso.query(':timebase:delay?'))
        print(f'Posición horizontal: {position} [s]')
        return position
    except Exception as e:
        print("Error al obtener la posición horizontal:", e)
        close_system(instrument)

def set_timebase_position(instrument, value):
    dso = instrument[1]
    try:
        dso.write(f':timebase:delay {value}')
        position = get_timebase_position(instrument)
        if position == value:
            print(f'Posición horizontal configurada a: {position} [s]')
        else:
            print('No se pudo configurar la posición horizontal.')
    except Exception as e:
        print("Error al configurar la posición horizontal:", e)
        close_system(instrument)

def set_trigger(instrument, trigger_mode):
    dso = instrument[1]
    try:
        dso.write(trigger_mode)
        print("Modo de disparo configurado exitosamente.")
    except Exception as e:
        print("Error al configurar el modo de disparo:", e)
        close_system(instrument)

def get_trigger_level(instrument):
    dso = instrument[1]
    try:
        level = float(dso.query(':trigger:level?'))
        return level
    except Exception as e:
        print("Error al obtener el nivel de disparo:", e)
        close_system(instrument)

def set_trigger_level(instrument, trigger_level):
    dso = instrument[1]
    try:
        dso.write(f':trigger:level {trigger_level}')
        if (get_trigger_level(instrument) == trigger_level):
            print(f"Nivel de disparo configurado: {trigger_level}")
        else:
            print("No se pudo configurar el nivel de disparo.")
    except Exception as e:
        print("Error al configurar el nivel de disparo:", e)
        close_system(instrument)

def get_trigger_coupling(instrument):
    dso = instrument[1]
    couplings = ('AC', 'DC')
    try:
        coupling = dso.query(':trigger:couple?')
        print(f'Acoplamiento de trigger: {couplings[int(coupling)]}')
        return couplings[int(coupling)]
    except Exception as e:
        print("Error al obtener el acoplamiento de trigger:", e)
        close_system(instrument)

def set_trigger_coupling(instrument, coupling):
    dso = instrument[1]
    couplings = ('AC', 'DC')
    try:
        dso.write(f':trigger:couple {coupling}')
        current_coupling = get_trigger_coupling(instrument)
        if current_coupling == couplings[coupling]:
            print(f'Acoplamiento de trigger configurado a: {current_coupling}')
        else:
            print('No se pudo configurar el acoplamiento de trigger.')
    except Exception as e:
        print("Error al configurar el acoplamiento de trigger:", e)
        close_system(instrument)

def get_trigger_mode(instrument):
    dso = instrument[1]
    modes = ('Auto', 'Normal')
    try:
        mode = dso.query(':trigger:mode?')
        print(f'Modo de trigger: {modes[int(mode)-1]}')
        return modes[int(mode)-1]
    except Exception as e:
        print("Error al obtener el modo de trigger:", e)
        close_system(instrument)

def set_trigger_mode(instrument, mode):
    dso = instrument[1]
    modes = ('Auto', 'Normal')
    try:
        dso.write(f':trigger:mode {mode+1}')
        current_mode = get_trigger_mode(instrument)
        if current_mode == modes[mode]:
            print(f'Modo de trigger configurado a: {current_mode}')
        else:
            print('No se pudo configurar el modo de trigger.')
    except Exception as e:
        print("Error al configurar el modo de trigger:", e)
        close_system(instrument)

def get_trigger_nrej(instrument):
    dso = instrument[1]
    states = ('OFF', 'ON')
    try:
        nrej = dso.query(':trigger:nrej?')
        status = states[int(nrej)]
        print(f'Rechazo de ruido de trigger está {status}')
        return status
    except Exception as e:
        print("Error al obtener el estado de rechazo de ruido de trigger:", e)
        close_system(instrument)

def set_trigger_nrej(instrument, state):
    dso = instrument[1]
    states = ('OFF', 'ON')
    try:
        dso.write(f':trigger:nrej {state}')
        current_state = get_trigger_nrej(instrument)
        if current_state == states[int(state)]:
            print(f'Rechazo de ruido de trigger configurado a: {current_state}')
        else:
            print('No se pudo configurar el rechazo de ruido de trigger.')
    except Exception as e:
        print("Error al configurar el rechazo de ruido de trigger:", e)
        close_system(instrument)

def get_trigger_reject(instrument):
    dso = instrument[1]
    modes = ('OFF', 'LF', 'HF')
    try:
        rej = dso.query(':trigger:reject?')
        print(f'Filtro de ruido de trigger: {modes[int(rej)]}')
        return modes[int(rej)]
    except Exception as e:
        print("Error al obtener el filtro de ruido de trigger:", e)
        close_system(instrument)

def set_trigger_reject(instrument, mode):
    dso = instrument[1]
    modes = ('OFF', 'LF', 'HF')
    try:
        dso.write(f':trigger:reject {mode}')
        current_mode = get_trigger_reject(instrument)
        if current_mode == modes[mode]:
            print(f'Filtro de ruido de trigger configurado a: {current_mode}')
        else:
            print('No se pudo configurar el filtro de ruido de trigger.')
    except Exception as e:
        print("Error al configurar el filtro de ruido de trigger:", e)
        close_system(instrument)

def get_trigger_slope(instrument):
    dso = instrument[1]
    slopes = ('Positivo', 'Negativo')
    try:
        slope = dso.query(':trigger:slope?')
        print(f'Flanco de trigger: {slopes[int(slope)]}')
        return slopes[int(slope)]
    except Exception as e:
        print("Error al obtener el flanco de trigger:", e)
        close_system(instrument)

def set_trigger_slope(instrument, slope):
    dso = instrument[1]
    slopes = ('Positivo', 'Negativo')
    try:
        dso.write(f':trigger:slope {slope}')
        current_slope = get_trigger_slope(instrument)
        if current_slope == slopes[slope]:
            print(f'Flanco de trigger configurado a: {current_slope}')
        else:
            print('No se pudo configurar el flanco de trigger.')
    except Exception as e:
        print("Error al configurar el flanco de trigger:", e)
        close_system(instrument)

def get_trigger_state(instrument):
    dso = instrument[1]
    states = ('No disparado', 'Disparado')
    try:
        state = dso.query(':trigger:state?')
        print(f'Estado de trigger: {states[int(state)]}')
        return states[int(state)]
    except Exception as e:
        print("Error al obtener el estado de trigger:", e)
        close_system(instrument)

def get_triger_source(instrument):
    dso = instrument[1]
    sources = ('Canal 1', 'Canal 2', 'Externo', 'Red')
    try:
        source = dso.query(':trigger:source?')
        print(f'Fuente de trigger: {sources[int(source)]}')
        return sources[int(source)]
    except Exception as e:
        print("Error al obtener la fuente de trigger:", e)
        close_system(instrument)

def set_trigger_source(instrument, source):
    dso = instrument[1]
    sources = ('Canal 1', 'Canal 2', 'Externo', 'Red')
    try:
        dso.write(f':trigger:source {source}')
        current_source = get_triger_source(instrument)
        if current_source == sources[source]:
            print(f'Fuente de trigger configurada a: {current_source}')
        else:
            print('No se pudo configurar la fuente de trigger.')
    except Exception as e:
        print("Error al configurar la fuente de trigger:", e)
        close_system(instrument)

def get_trigger_type(instrument):
    dso = instrument[1]
    types = ('Edge', 'Video', 'Pulse')
    try:
        ttype = dso.query(':trigger:type?')
        print(f'Tipo de trigger: {types[int(ttype)]}')
        return types[int(ttype)]
    except Exception as e:
        print("Error al obtener el tipo de trigger:", e)
        close_system(instrument)

def set_trigger_type(instrument, ttype):
    dso = instrument[1]
    types = ('Edge', 'Video', 'Pulse')
    try:
        dso.write(f':trigger:type {ttype}')
        current_type = get_trigger_type(instrument)
        if current_type == types[ttype]:
            print(f'Tipo de trigger configurado a: {current_type}')
        else:
            print('No se pudo configurar el tipo de trigger.')
    except Exception as e:
        print("Error al configurar el tipo de trigger:", e)
        close_system(instrument)

def get_adquire_mode(instrument):
    dso = instrument[1]
    modes = ('Normal', 'Peak detect', 'Average')
    try:
        mode = dso.query(':acquire:mode?')
        print(f'Modo de adquisición: {modes[int(mode)]}')
        return modes[int(mode)]
    except Exception as e:
        print("Error al obtener el modo de adquisición:", e)
        close_system(instrument)

def set_adquire_mode(instrument, mode):
    dso = instrument[1]
    modes = ('Normal', 'Peak detect', 'Average')
    try:
        dso.write(f':acquire:mode {mode}')
        current_mode = get_adquire_mode(instrument)
        if current_mode == modes[mode]:
            print(f'Modo de adquisición configurado a: {current_mode}')
        else:
            print('No se pudo configurar el modo de adquisición.')
    except Exception as e:
        print("Error al configurar el modo de adquisición:", e)
        close_system(instrument)

def get_channel_coupling(instrument, channel):
    dso = instrument[1]
    couplings = ('AC', 'DC', 'GND')
    try:
        coupling = dso.query(f':channel{channel}:coupling?')
        print(f'Acoplamiento del canal 1: {couplings[int(coupling)]}')
        return couplings[int(coupling)]
    except Exception as e:
        print("Error al obtener el acoplamiento del canal:", e)
        close_system(instrument)

def set_channel_coupling(instrument, channel, coupling):
    dso = instrument[1]
    couplings = ('AC', 'DC', 'GND')
    try:
        dso.write(f':channel{channel}:coupling {coupling}')
        current_coupling = get_channel_coupling(instrument, channel)
        if current_coupling == couplings[coupling]:
            print(f'Acoplamiento del canal {channel} configurado a: {current_coupling}')
        else:
            print('No se pudo configurar el acoplamiento del canal.')
    except Exception as e:
        print("Error al configurar el acoplamiento del canal:", e)
        close_system(instrument)

def get_channel_display(instrument, channel):
    dso = instrument[1]
    states = ('OFF', 'ON')
    try:
        display = dso.query(f':channel{channel}:display?')
        status = states[int(display)]
        print(f'Canal {channel} está {status}')
        return status
    except Exception as e:
        print("Error al obtener el estado de visualización del canal:", e)
        close_system(instrument)

def set_channel_display(instrument, channel, state):
    dso = instrument[1]
    states = ('OFF', 'ON')
    try:
        dso.write(f':channel{channel}:display {state}')
        current_state = get_channel_display(instrument, channel)
        if current_state == states[int(state)]:
            print(f'Canal {channel} configurado a: {current_state}')
        else:
            print('No se pudo configurar el estado de visualización del canal.')
    except Exception as e:
        print("Error al configurar el estado de visualización del canal:", e)
        close_system(instrument)

def get_channel_offset(instrument, channel):
    dso = instrument[1]
    try:
        offset = float(dso.query(f':channel{channel}:offset?'))
        print(f'Offset del canal {channel}: {offset} [V]')
        return offset
    except Exception as e:
        print("Error al obtener el offset del canal:", e)
        close_system(instrument)

def set_channel_offset(instrument, channel, offset):
    dso = instrument[1]
    try:
        dso.write(f':channel{channel}:offset {offset}')
        current_offset = get_channel_offset(instrument, channel)
        if current_offset == offset:
            print(f'Offset del canal {channel} configurado a: {current_offset} [V]')
        else:
            print('No se pudo configurar el offset del canal.')
    except Exception as e:
        print("Error al configurar el offset del canal:", e)
        close_system(instrument)

def get_channel_attenuation(instrument, channel):
    dso = instrument[1]
    try:
        attenuation = float(dso.query(f':channel{channel}:probe:ratio?'))
        print(f'Factor de atenuación del canal {channel}: {attenuation}')
        return attenuation
    except Exception as e:
        print("Error al obtener el factor de atenuación del canal:", e)
        close_system(instrument)

def set_channel_attenuation(instrument, channel, attenuation):
    dso = instrument[1]
    try:
        dso.write(f':channel{channel}:probe:ratio {attenuation}')
        current_attenuation = get_channel_attenuation(instrument, channel)
        if current_attenuation == attenuation:
            print(f'Factor de atenuación del canal {channel} configurado a: {current_attenuation}')
        else:
            print('No se pudo configurar el factor de atenuación del canal.')
    except Exception as e:
        print("Error al configurar el factor de atenuación del canal:", e)
        close_system(instrument)

def get_channel_type(instrument, channel):
    dso = instrument[1]
    types = ('Tensión', 'Corriente')
    try:
        ctype = dso.query(f':channel{channel}:probe:type?')
        print(f'Tipo de prueba del canal {channel}: {types[int(ctype)]}')
        return types[int(ctype)]
    except Exception as e:
        print("Error al obtener el tipo de prueba del canal:", e)
        close_system(instrument)

def set_channel_type(instrument, channel, ctype):
    dso = instrument[1]
    types = ('Tensión', 'Corriente')
    try:
        dso.write(f':channel{channel}:probe:type {ctype}')
        current_type = get_channel_type(instrument, channel)
        if current_type == types[ctype]:
            print(f'Tipo de prueba del canal {channel} configurado a: {current_type}')
        else:
            print('No se pudo configurar el tipo de prueba del canal.')
    except Exception as e:
        print("Error al configurar el tipo de prueba del canal:", e)
        close_system(instrument)

def set_single_trigger(instrument):
    dso = instrument[1]
    try:
        dso.write(':single')
        print("Disparo único configurado exitosamente.")
    except Exception as e:
        print("Error al configurar el disparo único:", e)
        close_system(instrument)

def plot_waveform(waveform, dt):
    num_points = len(waveform)
    time_axis = np.linspace(0, (num_points - 1) * dt, num_points)
    plt.figure(figsize=(12, 6))
    plt.plot(time_axis, waveform)
    plt.title("Forma de Onda Adquirida")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Voltaje (V)")
    plt.grid(True)
    plt.show()

def close_instrument(dso):
    try:
        dso.close()
        print("Conexión con el instrumento cerrada exitosamente.")
    except Exception as e:
        print("Error al cerrar la conexión con el instrumento:", e)

def close_system(instrument):
    try:
        close_instrument(instrument[1])
        instrument[0].close()
        print("Gestor de recursos cerrado exitosamente.")
    except Exception as e:
        print("Error al cerrar el gestor de recursos:", e)