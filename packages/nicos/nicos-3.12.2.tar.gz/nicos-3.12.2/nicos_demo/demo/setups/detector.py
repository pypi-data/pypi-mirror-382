description = 'virtual detector'
group = 'lowlevel'

includes = ['system']
excludes = ['sans']

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        visibility = (),
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        visibility = (),
        type = 'monitor',
        countrate = 1000,
        fmtstr = '%d',
    ),
    ctr1 = device('nicos.devices.generic.VirtualCounter',
        visibility = (),
        type = 'counter',
        countrate = 2000,
        fmtstr = '%d',
    ),
    ctr2 = device('nicos.devices.generic.VirtualCounter',
        visibility = (),
        type = 'counter',
        countrate = 120,
        fmtstr = '%d',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = ['ctr1', 'ctr2'],
        maxage = 3,
        pollinterval = 0.5,
    ),
)

startupcode = '''
SetDetectors(det)
'''
