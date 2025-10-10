description = 'FRM II reactor status devices'

group = 'lowlevel'

tango_base = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/mlz/'

devices = dict(
    ReactorPower = device('nicos.devices.entangle.AnalogInput',
        description = 'FRM II reactor power',
        tangodevice = tango_base + 'reactor/power',
        warnlimits = (19, 21),
        fmtstr = '%.1f',
        pollinterval = 60,
        maxage = 3600,
        unit = 'MW'
    ),
)

extended = dict(
    representative = 'ReactorPower',
)
