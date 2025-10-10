description = 'STRESS-SPEC setup with Newport Eulerian cradle'

group = 'basic'

includes = [
    'standard',
    'sampletable',
]

sysconfig = dict(
    datasinks = ['caresssink', 'yamlsink'],
)

tango_base = 'tango://motorbox06.stressi.frm2.tum.de:10000/box/'

devices = dict(
    chis_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel3/motor',
        fmtstr = '%.2f',
        visibility = (),
    ),
    chis_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel3/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    chis = device('nicos.devices.generic.Axis',
        description = 'Eulerian Newport CHIS',
        motor = 'chis_m',
        coder = 'chis_c',
        precision = 0.01,
    ),
    phis_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel4/motor',
        fmtstr = '%.2f',
        visibility = (),
    ),
    phis = device('nicos.devices.generic.Axis',
        description = 'Eulerian Newport PHIS',
        motor = 'phis_m',
        precision = 0.01,
    ),
)
