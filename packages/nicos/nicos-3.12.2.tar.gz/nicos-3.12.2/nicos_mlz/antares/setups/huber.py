description = 'HUBER Sample Table Experimental Chamber 1'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    stx_huber = device('nicos.devices.entangle.Motor',
        description = 'Sample Translation X',
        tangodevice = tango_base + 'fzjs7/Probe_X',
        precision = 0.01,
        abslimits = (0, 400),
        pollinterval = 5,
        maxage = 12,
    ),
    sty_huber = device('nicos.devices.entangle.Motor',
        description = 'Sample Translation Y',
        tangodevice = tango_base + 'fzjs7/Probe_Y',
        precision = 0.01,
        abslimits = (0, 400),
        pollinterval = 5,
        maxage = 12,
    ),
    sgx_huber = device('nicos.devices.entangle.Motor',
        description = 'Sample Rotation around X',
        tangodevice = tango_base + 'fzjs7/Probe_tilt_x',
        precision = 0.01,
        abslimits = (-10, 10),
        pollinterval = 5,
        maxage = 12,
    ),
    sgz_huber = device('nicos.devices.entangle.Motor',
        description = 'Sample Rotation around Z',
        tangodevice = tango_base + 'fzjs7/Probe_tilt_z',
        precision = 0.01,
        abslimits = (-10, 10),
        pollinterval = 5,
        maxage = 12,
    ),
    sry_huber = device('nicos.devices.entangle.Motor',
        description = 'Sample Rotation around Y',
        tangodevice = tango_base + 'fzjs7/Probe_phi',
        precision = 0.01,
        abslimits = (-999999, 999999),
        pollinterval = 5,
        maxage = 12,
    ),
)

monitor_blocks = dict(
   default = Block('HUBER Small Sample Manipulator',
        [
            BlockRow(
                Field(dev='stx_huber'),
                Field(dev='sty_huber'),
                Field(dev='sry_huber'),
            ),
            BlockRow(
                Field(dev='sgx_huber'),
                Field(dev='sgz_huber'),
            ),
        ],
        setups=setupname
    ),
)
