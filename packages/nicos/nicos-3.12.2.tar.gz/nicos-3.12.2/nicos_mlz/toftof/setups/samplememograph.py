description = 'memograph readout for the sample cooling system'

group = 'lowlevel'

tango_base = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/memograph07/TOF1/'
system = 'sample'

devices = {
    't_in_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet temperature %s' % system,
        tangodevice = tango_base + 'T_in',
        fmtstr = '%.1f',
        warnlimits = (-1, 17.5), #-1 no lower value
        unit = 'degC',
    ),
    't_out_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet temperature %s' % system,
        tangodevice = tango_base + 'T_out',
        fmtstr = '%.1f',
        unit = 'degC',
    ),
    'p_in_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet pressure %s' % system,
        tangodevice = tango_base + 'P_in',
        fmtstr = '%.1f',
        unit = 'bar',
    ),
    'p_out_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet pressure %s' % system,
        tangodevice = tango_base + 'P_out',
        fmtstr = '%.1f',
        unit = 'bar',
    ),
    'flow_in_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet flow %s' % system,
        tangodevice = tango_base + 'FLOW_in',
        fmtstr = '%.1f',
        warnlimits = (0.2, 100), #100 no upper value
    ),
    'flow_out_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet flow %s' % system,
        tangodevice = tango_base + 'FLOW_out',
        fmtstr = '%.1f',
        unit = 'l/min',
    ),
    'leak_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        description = 'leakage %s' % system,
        tangodevice = tango_base + 'Leak',
        fmtstr = '%.1f',
        warnlimits = (-1, 1), #-1 no lower value
        unit = 'l/min',
    ),
    'power_%s_cooling' % system[:2]: device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'Cooling',
        description = 'Cooling power %s' % system,
        fmtstr = '%.1f',
        unit = 'kW',
    ),
}
