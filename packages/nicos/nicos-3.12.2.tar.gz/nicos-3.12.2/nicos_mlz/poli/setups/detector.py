description = 'POLI detector and counter card'
group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        tangodevice = tango_base + 'frmctr/timer',
        fmtstr = '%.2f',
        visibility = (),
    ),
    mon1 = device('nicos.devices.entangle.CounterChannel',
        tangodevice = tango_base + 'frmctr/ctr1',
        type = 'monitor',
        fmtstr = '%d',
        visibility = (),
    ),
    mon2 = device('nicos.devices.entangle.CounterChannel',
        tangodevice = tango_base + 'frmctr/ctr2',
        type = 'monitor',
        fmtstr = '%d',
        visibility = (),
    ),
    ctr1 = device('nicos.devices.entangle.CounterChannel',
        tangodevice = tango_base + 'frmctr/ctr0',
        type = 'counter',
        fmtstr = '%d',
        visibility = (),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'FRM II multichannel counter card',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        counters = ['ctr1'],
        maxage = 2,
        pollinterval = 1.0,
    ),
)

startupcode = '''
SetDetectors(det)
'''
