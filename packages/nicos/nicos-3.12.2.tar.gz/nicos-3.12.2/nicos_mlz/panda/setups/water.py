description = 'setup for water flow'
group = 'optional'
display_order = 11

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    water = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Water flux readout',
        tangodevice = tango_base + 'water/flow',
        fmtstr = '%s',
        mapping = {'off': 0,
                   'on': 1},
    ),
)
