description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

tango_base = 'tango://miractrl.mira.frm2.tum.de:10000/mira/'

devices = dict(
    dct1 = device('nicos.devices.entangle.PowerSupply',
        description = 'current in first channel of supply (flipper current)',
        tangodevice = tango_base + 'tti1/out1',
        timeout = 1,
        precision = 0.01,
    ),
    dct2 = device('nicos.devices.entangle.PowerSupply',
        description = 'current in second channel of supply (compensation current)',
        tangodevice = tango_base + 'tti1/out2',
        timeout = 1,
        precision = 0.01,
    ),
    flip = device('nicos.devices.polarized.MezeiFlipper',
        description = 'Mezei flipper before sample (in shielding table)',
        flip = 'dct1',
        corr = 'dct2',
    ),
)
