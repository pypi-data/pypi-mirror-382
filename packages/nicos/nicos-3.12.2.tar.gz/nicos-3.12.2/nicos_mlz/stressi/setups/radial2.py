description = 'Radialcollimator 2 devices'

group = 'optional'

includes = ['rad_fwhm']

excludes = ['radial']

tango_base = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/'

devices = dict(
    rcdet_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel8/motor',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rcdet_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel8/coder',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rcdet = device('nicos.devices.generic.Axis',
        description = 'RadColli 2',
        fmtstr = '%.3f',
        motor = 'rcdet_m',
        coder = 'rcdet_c',
        precision = 0.01,
    ),
)
