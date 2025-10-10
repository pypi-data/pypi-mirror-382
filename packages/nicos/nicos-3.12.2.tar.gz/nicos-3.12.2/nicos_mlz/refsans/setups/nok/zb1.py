description = 'Slit ZB1 using beckhoff controllers'

group = 'lowlevel'

includes = ['zz_absoluts']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index = 7

devices = dict(
    zb1 = device(code_base + 'slits.SingleSlit',
        # length: 13 mm
        description = 'zb1, singleslit at nok5b before nok6',
        unit = 'mm',
        motor = 'zb1_motor',
        offset = 0.0,
        nok_start = 5873.6,  # 5856.5
        nok_end = 5886.6,  # 5862.5
        # motor = 5880.1,
        masks = {
            'slit':    0,
            'point':   0,
            'gisans':  -110 * optic_values['gisans_scale'],
        },
    ),
    # zb1_a = device('nicos.devices.generic.Axis',
    #     description = 'zb1 axis',
    #     motor = 'zb1_motor',
    #     precision = 0.02,
    #     maxtries = 3,
    #     visibility() = (),
    # ),
    # zb1_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for ZB1 Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index*10, # word address
    #     abslimits = (-1000, 1000),
    #     visibility = showcase_values['hide_temp'],
    # ),
    # zb1_analog = device(code_base + 'beckhoff.nok.BeckhoffPoti',
    #     description = 'Poti for ZB1 no ref',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index*10, # word address
    #     abslimits = (-1000, 1000),
    #     poly =  [-283.16351478707793, 0.015860537603265893],
    #     visibility = () or showcase_values['hide_poti'],
    # ),
    # zb1_acc = device(code_base + 'accuracy.Accuracy',
    #      description = 'calc error Motor and poti',
    #      motor = 'zb1_motor',
    #      analog = 'zb1_analog',
    #      visibility = () or showcase_values['hide_acc'],
    #      unit = 'mm'
    # ),
)
