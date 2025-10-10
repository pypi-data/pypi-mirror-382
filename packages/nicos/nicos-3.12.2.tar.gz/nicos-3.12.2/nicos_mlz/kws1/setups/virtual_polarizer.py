description = 'Virtual polarizer setup'
group = 'lowlevel'
display_order = 60

devices = dict(
    polarizer = device('nicos_mlz.kws1.devices.polarizer.Polarizer',
        description = 'high-level polarizer switcher',
        switcher = 'pol_switch',
        flipper = 'flipper'
    ),
    pol_switch = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'switch polarizer or neutron guide',
        states = ['pol', 'ng'],
    ),
    flipper = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'spin flipper after polarizer',
        states = ['off', 'on'],
    ),
)

extended = dict(
    representative = 'polarizer',
)
