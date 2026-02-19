from gw_instek_gds1000a_u import *
#import time

if __name__ == '__main__':
    resource_manager = init_system()
    dso = init_instrument(resource_manager, 'ASRL6::INSTR')
    instrument = [resource_manager, dso]

    default_settings(instrument)
    set_channel_scale(instrument, 1, 1)
    set_timebase_scale(instrument, 5e-6)
    set_trigger_level(instrument, 520e-3)
    set_single_trigger(instrument)
    '''
    get_setting(instrument)
    default_settings(instrument)

    set_single_trigger(instrument)

    get_channel_type(instrument,1)
    set_channel_type(instrument, 1, 0)
    get_channel_attenuation(instrument, 1)
    set_channel_attenuation(instrument, 1, 1)
    get_channel_offset(instrument, 1)
    set_channel_offset(instrument, 1, 0)
    get_channel_display(instrument, 1)
    set_channel_display(instrument, 1, 1)
    get_channel_coupling(instrument, 1)
    set_channel_coupling(instrument, 1, 1)
    get_channel_scale(instrument, 1)
    set_channel_scale(instrument, 1, 1)

    get_timebase_scale(instrument)
    set_timebase_scale(instrument, 250e-6)
    get_timebase_position(instrument)
    set_timebase_position(instrument, 1e-3)

    get_adquire_mode(instrument)
    set_adquire_mode(instrument, 2)

    get_trigger_level(instrument)
    set_trigger_level(instrument, 520e-3)
    get_trigger_coupling(instrument)
    set_trigger_coupling(instrument, 1)
    get_trigger_mode(instrument)
    set_trigger_mode(instrument, 1)
    get_trigger_nrej(instrument)
    set_trigger_nrej(instrument, 1)
    get_trigger_reject(instrument)
    set_trigger_reject(instrument, 1)
    get_trigger_slope(instrument)
    set_trigger_slope(instrument, 0)
    get_trigger_state(instrument)
    get_triger_source(instrument)
    set_trigger_source(instrument, 0)
    get_trigger_type(instrument)
    set_trigger_type(instrument, 0)
    '''
    #t0 = time.time()
    wave_form, dt = get_block_data(instrument, 1)
    #print(wave_form)
    if wave_form is not None:
        plot_waveform(wave_form, dt)
    #t1 = time.time()
    #print(f"Tiempo de adquisición y almacenamiento: {t1 - t0:.2f} [s]")

    close_system(instrument)