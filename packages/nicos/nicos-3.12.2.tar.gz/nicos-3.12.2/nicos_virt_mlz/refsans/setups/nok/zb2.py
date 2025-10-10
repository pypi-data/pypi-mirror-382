description = "SingleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

devices = dict(
    zb2 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 6.0 mm
        description = 'zb2 single Slit at nok6 before nok7',
        unit = 'mm',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-215.69, 93.0),
            unit = 'mm',
            speed = 1.,
            curvalue = -2,
        ),
        nok_start = 7633.5,  # 7591.5
        nok_end = 7639.5,  # 7597.5
        nok_gap = 1.0,
        offset = 0.0,
        # nok_motor = 7597.5,
        masks = {
            'slit':     -2,
            'point':   -2,
            'gisans':    -122.0,
        },
    ),
)
