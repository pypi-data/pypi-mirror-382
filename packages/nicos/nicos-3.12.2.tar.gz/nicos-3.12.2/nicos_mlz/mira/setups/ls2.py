description = 'LakeShore 340 cryo controller'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://miractrl.mira.frm2.tum.de:10000/mira/'

devices = dict(
    T_ls2 = device('nicos.devices.entangle.TemperatureController',
        description = 'temperature regulation',
        tangodevice = tango_base + 'ls2/ls_control1',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ls2_A = device('nicos.devices.entangle.Sensor',
        description = 'sensor A',
        tangodevice = tango_base + 'ls2/ls_sensor1',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ls2_B = device('nicos.devices.entangle.Sensor',
        description = 'sensor B',
        tangodevice = tango_base + 'ls2/ls_sensor2',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ls2_C = device('nicos.devices.entangle.Sensor',
        description = 'sensor C',
        tangodevice = tango_base + 'ls2/ls_sensor3',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_ls2_D = device('nicos.devices.entangle.Sensor',
        description = 'sensor D',
        tangodevice = tango_base + 'ls2/ls_sensor4',
        pollinterval = 0.7,
        maxage = 2,
    ),
)

alias_config = {
    'T': {'T_ls2': 180},  # lower than default CCR
    'Ts': {'T_ls2_A': 60, 'T_ls2_B': 50},
}
