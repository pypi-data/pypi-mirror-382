description = 'setup for Eurotherm sample heater'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_et = device('nicos.devices.entangle.TemperatureController',
        description = 'Eurotherm temperature controller',
        tangodevice = tango_base + 'eurotherm/control',
        abslimits = (0, 200),
        precision = 0.1,
    ),
)

# When used as an additional sensor, the ET controller should not
# be used as T, but as Ts.  Julabo has 100 for both priorities.
alias_config = dict(T={'T_et': 90}, Ts={'T_et': 120})

extended = dict(
    representative = 'T_et',
)
