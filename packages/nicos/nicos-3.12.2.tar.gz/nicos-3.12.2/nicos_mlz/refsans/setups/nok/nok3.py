description = "neutronguide, radialcollimator"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok3 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 600.0 mm
        description = 'NOK3',
        fmtstr = '%.2f, %.2f',
        nok_start = 680.0,
        nok_end = 1280.0,
        nok_gap = 1.0,
        inclinationlimits = (-20, 20),
        motor_r = 'nok3r_axis',
        motor_s = 'nok3s_axis',
        nok_motor = [831.0, 1131.0],
        precision = 0.0,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['rc'],
            'vc': optic_values['ng'],
            'fc': optic_values['ng'],
        },
    ),
    nok3r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK3, reactor side',
        motor = 'nok3r_motor',
        # obs = ['nok3r_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok3r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok3r_motor',
         device2 = 'nok3r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    nok3r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK3, reactor side',
        reference = 'nok_refa1',
        measure = 'nok3r_poti',
        poly = [21.830175, 997.962 / 3.846],
        serial = 6507,
        length = 250.0,
        visibility = showcase_values['hide_poti'],
    ),
    nok3r_poti = device(code_base + 'nok_sensor.NOKMonitoredVoltage',
        description = 'Poti for NOK3, reactor side',
        tangodevice = tango_base + 'test/wb_a/1_3',
        scale = 1,   # mounted from bottom
        visibility = (),
    ),
    nok3s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK3, sample side',
        motor = 'nok3s_motor',
        # obs = ['nok3s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok3s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok3s_motor',
         device2 = 'nok3s_analog',
         visibility = showcase_values['hide_acc'],
    ),
    nok3s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK3, sample side',
        reference = 'nok_refa1',
        measure = 'nok3s_poti',
        poly = [10.409698, 1003.196 / 3.854],
        serial = 6506,
        length = 250.0,
        visibility = showcase_values['hide_poti'],
    ),
    nok3s_poti = device(code_base + 'nok_sensor.NOKMonitoredVoltage',
        description = 'Poti for NOK3, sample side',
        tangodevice = tango_base + 'test/wb_a/1_4',
        scale = 1,   # mounted from bottom
        visibility = (),
    ),
)
