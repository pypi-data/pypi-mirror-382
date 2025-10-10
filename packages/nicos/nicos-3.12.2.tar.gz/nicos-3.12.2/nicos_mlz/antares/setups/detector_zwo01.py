description = 'ZWO CCD camera 1 devices'

group = 'lowlevel'

tango_base = 'tango://zwo01.antares.frm2.tum.de:10000/zwo/camera/'

devices = dict(
    zwo01 = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera 1',
        tangodevice = tango_base + '1',
        visibility = (),
        flip = (True, False),
    ),
    timer_zwo01 = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + '1',
        visibility = (),
    ),
    det_zwo01 = device('nicos.devices.generic.Detector',
        description = 'Camera 1 base detector',
        images = ['zwo01'],
        timers = ['timer_zwo01'],
    ),
    temp_zwo01 = device('nicos.devices.vendor.lima.ZwoTC',
        description = 'Temperature of CCD sensor chip cam 1',
        tangodevice = tango_base + 'cooler',
        abslimits = (-30, 30),
        precision = 0.5,
        unit = 'degC',
    ),
)
