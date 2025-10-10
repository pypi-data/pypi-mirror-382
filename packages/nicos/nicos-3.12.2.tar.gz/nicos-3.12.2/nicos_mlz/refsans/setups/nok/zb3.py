description = "DoubleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    zb3 = device(code_base + 'slits.DoubleSlit',
        description = 'ZB3 slit',
        slit_r = 'zb3r',
        slit_s = 'zb3s',
        fmtstr = 'zpos: %.3f, open: %.3f',
        unit = 'mm',
    ),
    zb3r = device(code_base + 'slits.SingleSlit',
        # length: 13.0 mm
        description = 'ZB3 slit, reactor side',
        motor = 'zb3r_axis',
        nok_start = 8856.5, # 8837.5,
        nok_end = 8869.5, # 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': -1.8,  # 2021-03-17 16:05:10 TheoMH -0.3,
            'point': -1.8,  # 2021-03-17 16:05:10 TheoMH -0.3,
            'gisans': -110.15 * optic_values['gisans_scale'],
        },
        unit = 'mm',
        visibility = (),
    ),
    zb3s = device(code_base + 'slits.SingleSlit',
        # length: 13.0 mm
        description = 'ZB3 slit, sample side',
        motor = 'zb3s_axis',
        nok_start = 8856.5, # 8837.5,
        nok_end = 8869.5, # 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': 0.3,  # 2021-03-17 16:05:10 TheoMH -1.4
            'point': 0.3,  # 2021-03-17 16:05:10 TheoMH -1.4
            'gisans': 0.3,  # 2021-03-17 16:05:10 TheoMH -1.4
        },
        unit = 'mm',
        visibility = (),
    ),
    zb3r_axis = device('nicos.devices.generic.Axis',
        description = 'ZB3 slit, reactor side for backlash',
        motor = 'zb3r_motor',
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    zb3s_axis = device('nicos.devices.generic.Axis',
        description = 'ZB3 slit, sample side for backlash',
        motor = 'zb3s_motor',
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    zb3r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'zb3r_motor',
         device2 = 'zb3r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    zb3r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for ZB3, reactor side',
        reference = 'nok_refc1',
        measure = 'zb3r_poti',
        poly = [-140.539293, 1004.824 / 1.92],
        serial = 7778,
        length = 500.0,
        visibility = showcase_values['hide_poti'] & showcase_values['NOreference'],
    ),
    zb3r_poti = device(code_base + 'nok_sensor.NOKMonitoredVoltage',
        description = 'Poti for ZB3, reactor side',
        tangodevice = tango_base + 'test/wb_c/1_2',
        scale = -1,  # mounted from top
        visibility = (),
    ),
    zb3s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'zb3s_motor',
         device2 = 'zb3s_analog',
         visibility = showcase_values['hide_acc'],
    ),
    zb3s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for ZB3, sample side',
        reference = 'nok_refc1',
        measure = 'zb3s_poti',
        poly = [118.68, 1000. / 1.921],
        serial = 7781,
        length = 500.0,
        visibility = showcase_values['hide_poti'] & showcase_values['NOreference'],
    ),
    zb3s_poti = device(code_base + 'nok_sensor.NOKMonitoredVoltage',
        description = 'Poti for ZB3, sample side',
        tangodevice = tango_base + 'test/wb_c/1_3',
        scale = 1,   # mounted from bottom
        visibility = (),
    ),
)

alias_config = {
    'primary_aperture': {'zb3.opening': 100},
}
