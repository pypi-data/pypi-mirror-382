description = 'Cryostat Compressor Control Box'
group = 'optional'

devices = dict(
    compressor = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Powerswitch of the cryostat compressor',
        tangodevice =
        'tango://antareshw.antares.frm2.tum.de:10000/antares/pumacc/pumacc_compressor',
        mapping = dict(On = 1, Off = 0),
    ),
)
