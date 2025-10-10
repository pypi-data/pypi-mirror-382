description = 'Cell pressure freezedrying'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    cell_pressure = device('nicos.devices.entangle.Sensor',
        description = 'cell pressure',
        tangodevice = tango_base + 'pressure/freezedrying',
    ),
)
