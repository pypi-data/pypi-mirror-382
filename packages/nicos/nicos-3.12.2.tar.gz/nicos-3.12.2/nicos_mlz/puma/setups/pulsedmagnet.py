description = 'Pulsed magnet'

group = 'optional'

tango_host = 'tango://puma5.puma.frm2.tum.de:10000/puma/'

includes = ['nanovoltmeter']

devices = dict(
    B_pm = device('nicos.devices.entangle.Sensor',
        description = 'Hall sensor',
        tangodevice = tango_host + 'magnet/field',
    ),
    B_current = device('nicos.devices.entangle.PowerSupply',
        description = 'Current through magnet coils',
        tangodevice = tango_host + 'ps/current',
    ),
)
