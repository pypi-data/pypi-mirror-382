description = 'light in ANTARES bunker'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    light = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'light in ANTARES bunker',
        tangodevice = tango_base + 'fzjdp_digital/LichtBunker',
        mapping = dict(on = 1, off = 0),
        unit = '',
    ),
)
