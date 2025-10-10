description = 'Andor IKON-L CCD camera emulation'
group = 'optional'

includes = ['shutters', 'filesavers']

devices = dict(
    timer_ikonl = device('nicos.devices.generic.VirtualTimer',
        description = 'The camera\'s internal timer',
        visibility = (),
    ),
    ikonl = device('nicos.devices.generic.VirtualImage',
        description = 'Demo 2D detector',
        fmtstr = '%d',
        size = (1024, 1024),
        visibility = (),
    ),
    temp_ikonl = device('nicos.devices.generic.VirtualTemperature',
        description = 'The CCD chip temperature',
        abslimits = (-100, 0),
        warnlimits = (None, 0),
        speed = 6,
        unit = 'degC',
        maxage = 5,
        fmtstr = '%.0f',
    ),
    det_ikonl = device('nicos.devices.generic.Detector',
        description = 'The Andor Ikon L CCD camera detector',
        images = ['ikonl'],
        timers = ['timer_ikonl'],
    ),
    sharpness = device('nicos_mlz.antares.devices.detector.Sharpness',
        description = 'Sharpness signal from the detector image'
    ),
    det_sharp = device('nicos.devices.generic.Detector',
        description = 'The Andor Ikon L CCD camera detector with sharpness detection',
        images = ['ikonl'],
        timers = ['timer_ikonl'],
        counters = ['sharpness'],
        postprocess = [('sharpness', 'ikonl')],
    ),
)

startupcode = """
SetDetectors(det_ikonl)
"""
