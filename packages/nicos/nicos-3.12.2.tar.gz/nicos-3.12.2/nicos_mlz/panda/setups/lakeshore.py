description = 'LakeShore 340 cryo controller'

includes = ['alias_T']
group = 'optional'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    T_ls340 = device('nicos.devices.entangle.TemperatureController',
        description = 'PANDA lakeshore controller',
        tangodevice = tango_base + 'ls340/control',
        maxage = 2,
        abslimits = (0, 300),
    ),
    T_ls340_A = device('nicos.devices.entangle.Sensor',
        description = 'PANDA lakeshore Sensor A',
        tangodevice = tango_base + 'ls340/sensora',
        maxage = 2,
    ),
    T_ls340_B = device('nicos.devices.entangle.Sensor',
        description = 'PANDA lakeshore Sensor B',
        tangodevice = tango_base + 'ls340/sensorb',
        maxage = 2,
    ),
    T_ls340_C = device('nicos.devices.entangle.Sensor',
        description = 'PANDA lakeshore Sensor C',
        tangodevice = tango_base + 'ls340/sensorc',
        maxage = 2,
    ),
    T_ls340_D = device('nicos.devices.entangle.Sensor',
        description = 'PANDA lakeshore Sensor D',
        tangodevice = tango_base + 'ls340/sensord',
        maxage = 2,
    ),
    ls340_heaterpower = device('nicos.devices.entangle.AnalogOutput',
        description = 'PANDA heater switch',
        tangodevice = tango_base + 'ls340/heater',
        maxage = 2,
    ),
    compressor_switch = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'PANDA cryo compressor switch',
        tangodevice = tango_base + 'ls340/relay1',
        mapping = {'off': 0,
                   'on': 1},
    ),
)

alias_config = {
    # give priority to sample-env T aliases
    'T': {'T_ls340': 190},
    'Ts': {'T_ls340_B': 95, 'T_ls340_A': 85, 'T_ls340_C': 75, 'T_ls340_D': 65},
}
