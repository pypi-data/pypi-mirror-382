description = 'Graphite filter devices'

group = 'lowlevel'

tango_base = 'tango://%s:10000/spodi/filterbox/' % 'spodictrl.spodi.frm2.tum.de'

devices = dict(
    filter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Graphite filter device',
        tangodevice = tango_base + 'filter_filterinout',
        mapping = {'in': 1,
                   'out': 0},
    ),
)
