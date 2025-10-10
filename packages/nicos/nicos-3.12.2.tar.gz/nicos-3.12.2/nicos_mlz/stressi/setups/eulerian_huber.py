description = 'STRESS-SPEC setup with Huber Eulerian cradle'

group = 'basic'

includes = [
    'standard',
    'sampletable',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

tango_base = 'tango://motorbox06.stressi.frm2.tum.de:10000/box/'

devices = dict(
    chis_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel1/motor',
        fmtstr = '%.2f',
        visibility = (),
    ),
    chis_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel1/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    chis = device('nicos.devices.generic.Axis',
        description = 'Eulerian Huber CHIS',
        motor = 'chis_m',
        coder = 'chis_c',
        precision = 0.01,
    ),
    phis_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel2/motor',
        fmtstr = '%.2f',
        userlimits = (-700, 700),
        visibility = (),
    ),
    phis_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel2/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    phis = device('nicos.devices.generic.Axis',
        description = 'Eulerian Huber PHIS',
        motor = 'phis_m',
        coder = 'phis_c',
        precision = 0.01,
    ),
)
