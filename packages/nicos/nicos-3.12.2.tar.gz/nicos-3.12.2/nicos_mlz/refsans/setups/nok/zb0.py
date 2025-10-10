description = 'Slit ZB0 using Beckhoff controllers'

group = 'lowlevel'

includes = ['zz_absoluts']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index = 4

devices = dict(
    # zb0_a = device('nicos.devices.generic.Axis',
    #     description = 'zb0 axis',
    #     motor = 'zb0_motor',
    #     precision = 0.02,
    #     maxtries = 3,
    #     visibility = (),
    # ),
    zb0 = device(code_base + 'slits.SingleSlit',
        # length: 13 mm
        description = 'zb0, singleslit',
        motor = 'zb0_motor',
        nok_start = 4121.5,
        nok_end = 4134.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -110 * optic_values['gisans_scale'],
        },
        unit = 'mm',
    ),
    # zb0_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for ZB0 Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index*10, # word address
    #     abslimits = (-1000, 1000),
    #     visibility = showcase_values['hide_temp'],
    # ),
    # zb0_analog = device(code_base + 'beckhoff.nok.BeckhoffPoti',
    #     description = 'Poti for ZB0 no ref',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index*10, # word address
    #     abslimits = (-1000, 1000),
    #     poly = [-176.49512271969755, 0.00794154091586989],
    #     visibility = () or showcase_values['hide_poti'],
    # ),
    # zb0_acc = device(code_base + 'accuracy.Accuracy',
    #      description = 'calc error Motor and poti',
    #      motor = 'zb0_motor',
    #      analog = 'zb0_analog',
    #      visibility = () or showcase_values['hide_acc'],
    #      unit = 'mm'
    # ),
)
