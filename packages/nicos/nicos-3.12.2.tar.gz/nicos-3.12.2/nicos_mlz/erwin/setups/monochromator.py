description = 'Monochromator devices'

group = 'lowlevel'

includes = ['motorbus']

devices = dict(
    om_m = device('nicos.devices.vendor.ipc.Motor',
        bus = 'motorbus',
        addr = 67,
        slope = 200,
        unit = 'deg',
        abslimits = (-117, 117),
        zerosteps = 80000,
        visibility = (),
        steps = 26200,
        # confbyte = 104,
    ),
    mono_z = device('nicos.devices.vendor.ipc.Motor',
        bus = 'motorbus',
        addr = 68,
        slope = 100,
        unit = 'mm',
        abslimits = (-117, 117),
        zerosteps = 40000,
        visibility = (),
        steps = 9000,
        # confbyte = 104,
    ),
    # wiege = device('nicos.devices.vendor.ipc.Motor',
    #     bus = 'motorbus',
    #     addr = 69,
    #     slope = 200,
    #     unit = 'deg',
    #     abslimits = (-117, 117),
    #     zerosteps = 80000,
    #     visibility = (),
    #     steps = 9220,
    #     # confbyte = 104,
    # ),
)
