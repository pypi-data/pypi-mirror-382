description = 'setup for sample attenuator'
group = 'optional'
display_order = 30

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    sat_in = device('nicos.devices.entangle.DigitalInput',
        tangodevice = tango_base + 'sat/input',
        visibility = (),
    ),
    sat_out = device('nicos.devices.entangle.DigitalOutput',
        tangodevice = tango_base + 'sat/output',
        visibility = (),
    ),
    sat = device('nicos_mlz.panda.devices.satbox.SatBox',
        description = 'Sample beam attenuator',
        input = 'sat_in',
        output = 'sat_out',
        unit = 'mm',
        fmtstr = '%d',
        blades = [1, 2, 5, 10, 20],
        # blades = [0, 2, 5, 10, 20],  # code for nonworking blade
        readout = 'switches',
    ),
)
