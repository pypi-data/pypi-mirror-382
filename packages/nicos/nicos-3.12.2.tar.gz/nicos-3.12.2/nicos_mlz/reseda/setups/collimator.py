description = 'collimator'

group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2.tum.de:10000/reseda/iobox/'

devices = dict(
    coll_rot = device('nicos.devices.entangle.Motor',
        description = 'Rotation of collimator',
        tangodevice = tango_base + 'plc_coll_rot',
    ),
    coll_ang = device('nicos.devices.entangle.Motor',
        description = 'Tilt of collimator',
        tangodevice = tango_base + 'plc_coll_ang',
    ),
)
