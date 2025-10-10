description = 'ANTARES shutter devices'
group = 'optional'

excludes = ['fastshutter']

devices = dict(
    fastshutter_io = device('nicos.devices.generic.manual.ManualSwitch',
        states = [1, 2],
        visibility = (),
    ),
    fastshutter = device('nicos.devices.generic.Switcher',
        mapping = dict(open = 1, closed = 2),
        description = 'Virtual Fast Shutter',
        moveable = 'fastshutter_io',
        fallback = '<undefined>',
        precision = 0,
    ),
)
