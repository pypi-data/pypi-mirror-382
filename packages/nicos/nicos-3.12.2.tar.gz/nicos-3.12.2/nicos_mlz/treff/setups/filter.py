description = 'Be filter control'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'

devices = dict(
    be_filter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Beryllium filter',
        tangodevice = tango_base + 'FZJDP_Digital/BeFilter',
        mapping = {
            "in": 1,
            "out": 0,
        }
    ),
    be_heater = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Beryllium heater',
        tangodevice = tango_base + 'FZJDP_Digital/BeHeater',
        mapping = {
            "off": 0,
            "on": 1,
        }
    ),
    T_be_filter = device('nicos.devices.entangle.AnalogInput',
        description = 'Beryllium filter/crystal temperature',
        tangodevice = tango_base + 'FZJDP_Analog/TBeFilter',
        fmtstr = '%.0f',
        unit = 'K',
        pollinterval = 5,
        maxage = 6,
    ),
    T_be_heater = device('nicos.devices.entangle.AnalogInput',
        description = 'Beryllium heater temperature',
        tangodevice = tango_base + 'FZJDP_Analog/TBeHeater',
        fmtstr = '%.0f',
        unit = 'K',
        pollinterval = 5,
        maxage = 6,
        visibility = ('metadata', ),
    ),
    wavelength = device('nicos.devices.generic.ReadonlySwitcher',
        description = 'wavelength',
        readable = 'be_filter',
        mapping = {
            4.74: 'in',
            (4.74, 2.37): 'out',
        },
        fmtstr = '%.2f %.2f',
        unit = 'A',
        pollinterval = 5,
        maxage = 6,
    ),
    p_be_filter = device('nicos.devices.entangle.Sensor',
        description = 'Beryllium filter vacuum',
        tangodevice = tango_base + 'leybold/befilter',
    ),
    p_colli = device('nicos.devices.entangle.Sensor',
        description = 'Collimator vacuum',
        tangodevice = tango_base + 'leybold/collimation',
    ),
    p_guide = device('nicos.devices.entangle.Sensor',
        description = 'Neutron guide vacuum',
        tangodevice = tango_base + 'leybold/neutronguide',
    ),
)
