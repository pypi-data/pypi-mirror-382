description = 'Agilent multimeter'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    R_agilent_multimeter = device('nicos.devices.entangle.Sensor',
        description = 'Agilent multimeter: 4-wire resistance',
        tangodevice = tango_base + 'agilent_multimeter/fresistance',
    ),
)
