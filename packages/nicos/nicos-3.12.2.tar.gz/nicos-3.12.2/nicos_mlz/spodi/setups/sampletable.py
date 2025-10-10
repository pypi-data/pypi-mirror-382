description = 'sample table rotations'

group = 'lowlevel'

tango_base = 'tango://motorbox01.spodi.frm2.tum.de:10000/box/'

devices = dict(
    tths = device('nicos.devices.generic.Axis',
        description = 'TTHS',
        motor = device('nicos.devices.entangle.Motor',
            fmtstr = '%.3f',
            tangodevice = tango_base + 'tths/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            fmtstr = '%.3f',
            tangodevice = tango_base + 'tths/coder',
        ),
        precision = 0.005,
        maxtries = 10,
        backlash = 0.2,
    ),
    omgs = device('nicos.devices.generic.Axis',
        description = 'OMGS',
        motor = device('nicos.devices.entangle.Motor',
            fmtstr = '%.2f',
            tangodevice = tango_base + 'omgs/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            fmtstr = '%.2f',
            tangodevice = tango_base + 'omgs/enc',
        ),
        precision = 0.005,
    ),
)
