description = 'Setup of a Monochromator Focusing Box on PANDA'
group = 'lowlevel'
display_order = 22

extended = dict(dynamic_loaded = True)

devices = dict(
    # Nicos based access to phytron in magnet rack
    focimotorbus = device('nicos_mlz.panda.devices.mcc2.TangoSerial',
        tangodevice = 'tango://phys.panda.frm2:10000/panda/mcc/focibox',
        visibility = (),
    ),
    focibox = device('nicos_mlz.panda.devices.mcc2.MCC2Monoframe',
        bus = 'focimotorbus',
        description = 'reads monocodes and returns which mono is connected',
        addr = 0,
        unit = '',
    ),
    mfh = device('nicos.devices.generic.DeviceAlias',
        alias = '',
    ),
    mfv = device('nicos.devices.generic.DeviceAlias',
        alias = '',
    ),
)
