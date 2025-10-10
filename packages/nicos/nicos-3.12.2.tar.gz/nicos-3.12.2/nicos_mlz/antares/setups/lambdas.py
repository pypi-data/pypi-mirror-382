description = 'Lambda power supplies'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    I_lambda1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        precision = 0.04,
        timeout = 10,
    ),
    I_lambda2 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 2',
        tangodevice = tango_base + 'lambda2/current',
        precision = 0.04,
        timeout = 10,
    ),
    I_lambda3 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 3',
        tangodevice = tango_base + 'lambda3/current',
        precision = 0.05,
        timeout = 10,
    ),
    I_lambda4 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 4',
        tangodevice = tango_base + 'lambda4/current',
        precision = 0.15,
        timeout = 10,
    ),
)
