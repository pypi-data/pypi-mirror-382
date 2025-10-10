description = 'Beam shutter setup'
group = 'lowlevel'
display_order = 5

excludes = ['virtual_shutter']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'
tango_base_mlz = 'tango://ictrlfs.ictrl.frm2:10000/mlz/'

devices = dict(
    shutter_in = device('nicos.devices.entangle.DigitalInput',
        tangodevice = tango_base + 'sps/shutter_read',
        visibility = (),
    ),
    shutter_set = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'sps/shutter_write',
        visibility = (),
    ),
    shutter = device('nicos_mlz.kws1.devices.shutter.Shutter',
        description = 'shutter control',
        output = 'shutter_set',
        input = 'shutter_in',
        waittime = 1,
    ),
    nl3b_shutter = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Neutron guide 3b shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        tangodevice = tango_base_mlz + 'shutter/nl3b',
        pollinterval = 60,
        maxage = 120,
    ),
    sixfold_shutter = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Sixfold shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        tangodevice = tango_base_mlz + 'shutter/sixfold',
        pollinterval = 60,
        maxage = 120,
    ),
)

extended = dict(
    representative = 'shutter',
)
