description = 'Water-Julabo temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_julabo = device('nicos_mlz.kws1.devices.julabo.TemperatureController',
        description = 'The regulated temperature',
        tangodevice = tango_base + 'waterjulabo/control',
        abslimits = (5, 80),
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        timeout = 45 * 60.,
    ),
)

alias_config = {
    'T':  {'T_julabo': 100},
    'Ts': {'T_julabo': 100},
}

extended = dict(
    representative = 'T_julabo',
)
