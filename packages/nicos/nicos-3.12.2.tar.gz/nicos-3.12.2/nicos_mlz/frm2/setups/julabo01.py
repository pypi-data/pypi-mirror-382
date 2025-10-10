description = 'Julabo temperature controller'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base + 'julabo/control',
        abslimits = (-10, 140),
        precision = 0.1,
        fmtstr = '%.2f',
        unit = 'degC',
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 200},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)
