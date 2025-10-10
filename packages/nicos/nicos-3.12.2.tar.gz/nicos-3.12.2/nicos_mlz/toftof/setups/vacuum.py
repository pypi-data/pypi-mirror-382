description = 'chopper vacuum readout'

group = 'lowlevel'

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/vacuum/'

devices = dict(
    vac0 = device('nicos.devices.entangle.Sensor',
        description = 'Vacuum sensor in chopper vessel 1',
        tangodevice = tango_base + 'sens1',
        pollinterval = 10,
        maxage = 12,
    ),
    vac1 = device('nicos.devices.entangle.Sensor',
        description = 'Vacuum sensor in chopper vessel 2',
        tangodevice = tango_base + 'sens2',
        pollinterval = 10,
        maxage = 12,
    ),
    vac2 = device('nicos.devices.entangle.Sensor',
        description = 'Vacuum sensor in chopper vessel 3',
        tangodevice = tango_base + 'sens3',
        pollinterval = 10,
        maxage = 12,
    ),
    vac3 = device('nicos.devices.entangle.Sensor',
        description = 'Vacuum sensor in chopper vessel 4',
        tangodevice = tango_base + 'sens4',
        pollinterval = 10,
        maxage = 12,
    ),
)
