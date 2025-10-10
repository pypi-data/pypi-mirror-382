description = '3He detector'
group = 'optional'

includes = ['filesavers']

tango_base = 'tango://resedahw2.reseda.frm2.tum.de:10000/reseda'

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Timer channel 2',
        tangodevice = '%s/frmctr/timer' % tango_base,
        fmtstr = '%.2f',
        # visibility = (),
        unit = 's',
    ),
    monitor1 = device('nicos.devices.entangle.CounterChannel',
        description = 'Monitor channel 1',
        tangodevice = '%s/frmctr/counter0' % tango_base,
        type = 'monitor',
        fmtstr = '%d',
        # visibility = (),
        unit = 'cts'
    ),
    # monitor2 = device('nicos.devices.entangle.CounterChannel',
    #     description = 'Monitor channel 2',
    #     tangodevice = '%s/frmctr/counter1' % tango_base,
    #     type = 'monitor',
    #     fmtstr = '%d',
    #     visibility = (),
    # ),
    mon_hv = device('nicos.devices.entangle.PowerSupply',
        description = 'High voltage power supply of the monitor',
        tangodevice = '%s/mon/hv' % tango_base,
        abslimits = (0, 1050),
        unit = 'V',
    ),
    counter = device('nicos.devices.entangle.CounterChannel',
        description = 'Counter channel 1',
        tangodevice = '%s/frmctr/counter2' % tango_base,
        type = 'counter',
        fmtstr = '%d',
        # visibility = (),
        unit = 'cts',
    ),
)
