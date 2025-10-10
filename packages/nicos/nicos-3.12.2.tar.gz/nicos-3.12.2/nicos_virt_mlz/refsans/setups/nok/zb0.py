description = 'Slit ZB0 using Beckhoff controllers'

group = 'lowlevel'

lprecision = 0.01

devices = dict(
    zb0 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13 mm
        description = 'zb0, singleslit',
        motor = 'zb0_a',
        nok_start = 4138.8,  # 4121.5
        nok_end = 4151.8,  # 4134.5
        # motor = 4145.35,  # 4128.5
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -110,
        },
        unit = 'mm',
    ),
    zb0_a = device('nicos.devices.generic.Axis',
        description = 'zb0 axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-155.7889, 28.111099999999997),
            speed = 1.,
        ),
        precision = lprecision,
        maxtries = 3,
        visibility = (),
    ),
)
