description = 'Bruker 2.2T electromagnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'I_{setupname}': device('nicos.devices.entangle.PowerSupply',
        description = 'Magnet current',
        tangodevice = tango_base + 'bruker/supply',
        fmtstr = '%.1f',
        unit = 'A',
        timeout = 60.0,
        precision = 0.1,
    ),
    f'B_{setupname}': device('nicos.devices.generic.CalibratedMagnet',
        currentsource = f'I_{setupname}',
        description = 'Magnet field',
        # abslimits are automatically determined from I
        unit = 'T',
        fmtstr = '%.4f',
        # calibration from measurement of A. Feoktystov
        # during cycle 39, fitted 2016-09-19
        calibration = (
            1.2833,
            65.032,
            0.035235,
            -127.25,
            0.029687
        )
    ),
    f'{setupname}_sam_trans': device('nicos.devices.entangle.Motor',
        description = 'Sample changer stage',
        tangodevice = tango_base + 'plc/plc_motor',
        fmtstr = '%.1f',
        unit = 'mm',
        precision = 0.1,
    ),
}

alias_config = {
    'B': {f'B_{setupname}': 100, f'I_{setupname}': 80},
}

extended = dict(
    representative = f'B_{setupname}',
)
