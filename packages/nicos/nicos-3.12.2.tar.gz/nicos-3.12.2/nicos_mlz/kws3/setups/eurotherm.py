description = 'setup for Eurotherm sample heater'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    T_et = device('nicos.devices.entangle.TemperatureController',
        description = 'Eurotherm temperature controller',
        tangodevice = tango_base + 'eurotherm/control',
        precision = 0.1,
    ),
)

alias_config = dict(T={'T_et': 100})
