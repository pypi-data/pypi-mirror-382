description = 'Sample surface position measurement'

group = 'optional'

# includes = ['gonio']

instrument_values = configdata('instrument.values')
tango_url = instrument_values['tango_url'] % setupname
code_base = instrument_values['code_base'] + 'tristate.TriState'

devices = dict(
    height = device(code_base,
        description = 'Sample surface position.',
        unit = 'mm',
        port = 'height_port',
    ),
    height_port = device('nicos.devices.entangle.Sensor',
        description = 'Sample surface position',
        tangodevice = tango_url + 'box/keyence/sensor',
        unit = 'mm',
        visibility = (),
    ),
    sim_height = device('nicos.devices.generic.ManualMove',
        description = 'sim only',
        abslimits = (-10, 10),
        default = 0,
        fmtstr = '%.3f',
        unit = 'foo',
        visibility = (),
    ),
    sim_z = device('nicos.devices.generic.ManualMove',
        description = 'sim only',
        abslimits = (-10, 10),
        default = 0,
        fmtstr = '%.3f',
        unit = 'foo',
        visibility = (),
    ),
    active_regulator = device('nicos_mlz.reseda.devices.Regulator',
        description = 'todo',
        sensor = 'height',
        moveable = 'gonio_z',
        loopdelay = 1.0,
        maxstep = 0.1,
        minstep = 0.01,
        stepfactor = 1.0,
        unit = 'mm',
    ),
)
