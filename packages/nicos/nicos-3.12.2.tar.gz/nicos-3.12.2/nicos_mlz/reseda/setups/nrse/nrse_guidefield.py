description = 'Guide field for NRSE mode'
group = 'lowlevel'

tango_base = 'tango://heinzinger.reseda.frm2.tum.de:10000/box/heinzinger1'

devices = dict(
    guidefield = device('nicos.devices.entangle.PowerSupply',
        description = 'Guide field power supply (current regulated)',
        tangodevice = '%s/curr' % tango_base,
        fmtstr = '%.4f',
    ),
)
