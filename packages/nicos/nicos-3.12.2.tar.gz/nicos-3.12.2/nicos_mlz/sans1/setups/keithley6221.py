description = 'Keithley 6221 current source, for susceptometer measurements'
group = 'optional'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/sans1/'

devices = dict(
    keithley_ampl = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keithley amplitude',
        tangodevice = tango_base + 'keithley/ampl',
        unit = 'A',
    ),
    keithley_freq = device('nicos.devices.entangle.AnalogOutput',
        description = 'Keithley frequency',
        tangodevice = tango_base + 'keithley/freq',
        unit = 'Hz',
    ),
)
