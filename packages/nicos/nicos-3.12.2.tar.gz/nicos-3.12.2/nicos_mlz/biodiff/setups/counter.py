description = 'ZEA-2 counter card setup'
group = 'optional'

tango_base = 'tango://phys.biodiff.frm2:10000/biodiff/'

devices = dict(
    timer = device('nicos_mlz.jcns.devices.fpga.FPGATimerChannel',
        description = 'ZEA-2 counter card timer channel',
        tangodevice = tango_base + 'count/timer',
    ),
    mon1 = device('nicos.devices.entangle.CounterChannel',
        description = 'ZEA-2 counter card monitor channel',
        tangodevice = tango_base + 'count/mon1',
        type = 'monitor',
    ),
)
