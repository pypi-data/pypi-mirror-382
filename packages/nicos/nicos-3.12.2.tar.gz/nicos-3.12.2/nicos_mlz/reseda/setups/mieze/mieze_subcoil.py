description = 'Substraction coil for MIEZE mode'
group = 'lowlevel'
excludes = ['nrse_subcoil']

tango_base = 'tango://heinzinger.reseda.frm2.tum.de:10000/box/heinzinger'

devices = dict(
    subcoil_ps2 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current regulated powersupply 2',
        tangodevice = '%s2/curr' % tango_base,
        fmtstr = '%.4f',
    ),
)
