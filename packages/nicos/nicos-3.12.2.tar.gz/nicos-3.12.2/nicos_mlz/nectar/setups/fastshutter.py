description = 'Fast Shutter'
group = 'optional'

tango_base = 'tango://nectarhw.nectar.frm2.tum.de:10000/nectar'

devices = dict(
    fastshutter_io = device('nicos.devices.entangle.DigitalOutput',
        description = 'Beckhoff controlled fast shutter',
        tangodevice = '%s/shutter/plc_shutter' % tango_base,
        visibility = (),
    ),
    fastshutter = device('nicos.devices.generic.Switcher',
        description = 'Fast shutter',
        moveable = 'fastshutter_io',
        mapping = dict(open = 1, closed = 0),
        fallback = '<undefined>',
        precision = 0,
    ),
)

# XXX: use shutter in detecter (should be a GatedDetector) as gate

