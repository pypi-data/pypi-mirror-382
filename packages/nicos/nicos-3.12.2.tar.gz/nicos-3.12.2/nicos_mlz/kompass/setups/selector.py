description = 'Selector related devices'

group = 'lowlevel'

tango_base = 'tango://kompasshw.kompass.frm2.tum.de:10000/kompass/'

devices = dict(
    nvslift_m = device('nicos.devices.entangle.Motor',
        description = 'Neutron selector lift motor',
        tangodevice = tango_base + 'lift/motor',
        visibility = (),
    ),
    nvslift_c = device('nicos.devices.entangle.Sensor',
        description = 'Selector lift coder',
        tangodevice = tango_base + 'lift/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    nvslift_ax = device('nicos.devices.generic.Axis',
        description = 'Selector lift position',
        motor = 'nvslift_m',
        coder = 'nvslift_c',
        fmtstr = '%.2f',
        precision = 0.1,
        visibility = (),
    ),
    nvslift = device('nicos.devices.generic.Switcher',
        description = 'Neutron selector lift',
        moveable = 'nvslift_ax',
        mapping = {
            'out': 0.,
            'in': 405.377,
        },
        fallback = '',
        fmtstr = '%s',
        precision = 1.0,
        blockingmove = False,
        unit = 'mm',
    ),
)
