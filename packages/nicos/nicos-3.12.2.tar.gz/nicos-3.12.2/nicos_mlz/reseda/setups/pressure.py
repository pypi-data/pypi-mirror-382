description = 'Pressure sensors'
group = 'optional'

#includes = ['alias_T']

tango_base = 'tango://resedahw2.reseda.frm2.tum.de:10000/reseda'

devices = dict(
    P_ng_elements = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in the neutron guide elements',
        tangodevice = '%s/pressure/ng_elements' % tango_base,
        fmtstr = '%.1f',
        unit = 'mbar',
        warnlimits = (0, 10),
    ),
    P_polarizer = device('nicos.devices.entangle.Sensor',
        description = 'Polarizer pressure',
        tangodevice = '%s/pressure/polarizer' % tango_base,
        fmtstr = '%.1f',
        unit = 'mbar',
        warnlimits = (0, 1),
    ),
    P_selector_vacuum = device('nicos.devices.entangle.Sensor',
        description = 'Selector vacuum pressure',
        tangodevice = '%s/pressure/selector_vacuum' % tango_base,
        fmtstr = '%.4f',
        unit = 'mbar',
        warnlimits = (0, 0.001),
    ),
)
