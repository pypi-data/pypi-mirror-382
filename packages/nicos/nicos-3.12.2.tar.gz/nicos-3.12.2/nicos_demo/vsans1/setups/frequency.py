description = 'frequency counter, fg1 and fg2'

excludes = ['tisane_multifg']

# group = 'lowlevel'

devices = dict(
    # tisane_fg1_sample = device('nicos_mlz.sans1.devices.tisane.Burst',
    #     description = "Signal-generator for sample tisane signal",
    #     tangodevice = "%s/fg1_burst" % tango_base,
    #     frequency = 1000,
    #     amplitude = 2.5,
    #     offset = 1.3,
    #     shape = 'square',
    #     duty = 50,
    #     mapping = dict(On = 1, Off = 0),
    # ),
    # tisane_fg2_det = device('nicos_mlz.sans1.devices.tisane.Burst',
    #     description = "Signal-generator for detector tisane signal",
    #     tangodevice = "%s/fg2_burst" % tango_base,
    #     frequency = 1000,
    #     amplitude = 5.0,
    #     offset = 1.3,
    #     shape = 'square',
    #     duty = 50,
    #     mapping = dict(On = 1, Off = 0),
    # ),
)
