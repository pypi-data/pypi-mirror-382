description = 'Beryllium filter'
group = 'optional'
display_order = 31

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    TBeFilter = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'analyzer/plc_befiltertemp',
        warnlimits = (0, 80),
        unit = 'K',
        description = 'Temperature of the Be-Filter or 1513.4K if not used',
    ),
)
