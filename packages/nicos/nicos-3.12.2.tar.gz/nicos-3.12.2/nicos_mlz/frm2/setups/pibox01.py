description = 'piface box'
group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/piface/'

devices = dict(
    in_all = device('nicos.devices.entangle.DigitalInput',
        description = 'All inputs in one device',
        tangodevice = tango_base + 'in_all',
        maxage = 5,
        fmtstr = '0x%02x',
        pollinterval = 2,
    ),
    out_all = device('nicos.devices.entangle.DigitalOutput',
        description = 'All outputs in one device',
        tangodevice = tango_base + 'out_all',
        maxage = 5,
        fmtstr = '0x%02x',
        pollinterval = 2,
    ),
)

for i in range(8):
    devices['in_%d' % i] = device('nicos.devices.entangle.DigitalInput',
        description = '%d. Input' % i,
        tangodevice = tango_base + 'in_%d' % i,
        maxage = 5,
        pollinterval = 2,
        fmtstr = '%d',
    )
    devices['out_%d' % i] = device('nicos.devices.entangle.DigitalOutput',
        description = '%d. Output' % i,
        tangodevice = tango_base + 'out_%d' % i,
        maxage = 5,
        pollinterval = 2,
        fmtstr = '%d',
    )
