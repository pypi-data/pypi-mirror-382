description = 'Andor IKON-L CCD camera'
group = 'optional'

includes = ['shutters', 'filesavers']

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    timer_ikonl = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = 'The camera\'s internal timer',
        tangodevice = tango_base + 'detector/limaccd',
    ),
    det_ikonl = device('nicos.devices.generic.Detector',
        description = 'The Andor IKON L CCD camera detector',
        images = ['ikonl'],
        timers = ['timer_ikonl'],
    ),
    ikonl = device('nicos_mlz.antares.devices.detector.IkonLCCD',
        description = 'The Andor Ikon L CCD camera',
        tangodevice = tango_base + 'detector/limaccd',
        hwdevice = tango_base + 'detector/ikonl',
        fastshutter = 'fastshutter',
        pollinterval = 3,
        maxage = 9,
        flip = (False, True),
        rotation = 90,
        shutteropentime = 0.05,
        shutterclosetime = 0.05,
        shuttermode = 'auto',
        vsspeed = 38.55,
        hsspeed = 1,
        pgain = 4,
    ),
    temp_ikonl = device('nicos.devices.vendor.lima.Andor2TemperatureController',
        description = 'The CCD chip temperature',
        tangodevice = tango_base + 'detector/ikonl',
        maxage = 5,
        abslimits = (-100, 0),
        userlimits = (-100, 0),
        unit = 'degC',
        precision = 3,
        fmtstr = '%.0f',
    ),
)

startupcode = '''
SetDetectors(det_ikonl)

## override hw setting to known good values.
ikonl.rotation = 90
ikonl.shutteropentime = 0.05
ikonl.shutterclosetime = 0.05
ikonl.shuttermode = 'auto'
ikonl.vsspeed = 38.55
ikonl.hsspeed = 1
ikonl.pgain = 1
'''
