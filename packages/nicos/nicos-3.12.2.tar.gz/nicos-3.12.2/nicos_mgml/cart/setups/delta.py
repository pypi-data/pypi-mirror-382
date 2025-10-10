description = 'Reading Keithley multimeter as a counter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'

includes = ['busk6221']

devices = dict(
    #busk7001 = device('nicos.devices.entangle.StringIO',
    #    tangodevice = tango_base + 'k7001/io',
    #    loglevel = 'info',
    #    visibility = (),
    #),
    Delta = device('nicos_mgml.devices.keithley.Deltameter',
        description = 'Deltameter',
        fmtstr = '%.8f',
        k6221 = 'busk6221',
        k7001 = None, #'busk7001',
    ),
)
