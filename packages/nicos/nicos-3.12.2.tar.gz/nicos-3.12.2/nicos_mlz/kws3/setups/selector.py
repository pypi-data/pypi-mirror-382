description = 'Selector area setup'
group = 'lowlevel'
display_order = 20

excludes = ['virtual_selector']

sel_presets = configdata('config_selector.SELECTOR_PRESETS')

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

# TODO (later): add sel_rot to switcher devices
devices = dict(
    selector = device('nicos.devices.generic.MultiSwitcher',
        description = 'select selector presets',
        blockingmove = False,
        moveables = ['sel_lambda'],
        mapping = {k: [v['lam']] for (k, v) in sel_presets.items()},
        fallback = 'unknown',
        precision = [0.05],
    ),
    sel_speed = device('nicos.devices.entangle.Actuator',
        description = 'selector speed',
        tangodevice = tango_base + 's7_io/selector',
        abslimits = (60, 300),
        precision = 0.5,
        unit = 'Hz',
    ),
    sel_lambda = device('nicos_mlz.kws1.devices.selector.SelectorLambda',
        description = 'Selector wavelength control',
        seldev = 'sel_speed',
        unit = 'A',
        fmtstr = '%.2f',
        constant = 3133.4 / 60,  # SelectorLambda uses RPM
        offset = -0.00195,
    ),
    sel_rot = device('nicos.devices.entangle.Motor',
        description = 'selector rotation table',
        tangodevice = s7_motor + 'sel_rot',
        unit = 'deg',
        precision = 0.01,
        visibility = (),
    ),
)

extended = dict(
    representative = 'selector',
)
