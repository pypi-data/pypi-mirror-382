description = 'Guide field Helmholtz coils around sample position'
group = 'optional'

tango_base = 'tango://miractrl.mira.frm2.tum.de:10000/mira/'

devices = dict(
    dct5 = device('nicos.devices.entangle.PowerSupply',
        description = 'current in first channel of supply',
        tangodevice = tango_base + 'tticoil/out1',
        timeout = 2.5,
        precision = 0.01,
    ),
    dct6 = device('nicos.devices.entangle.PowerSupply',
        description = 'current in second channel of supply',
        tangodevice = tango_base + 'tticoil/out2',
        timeout = 2.5,
        precision = 0.01,
    ),
)
