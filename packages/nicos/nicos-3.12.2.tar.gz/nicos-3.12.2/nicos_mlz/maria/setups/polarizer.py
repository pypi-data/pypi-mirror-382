description = "Polarizer setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_s7 = tango_base + "/FZJS7"
tango_dio = tango_base + "/FZJDP_Digital"
tango_ps = tango_base + "/toellner"

devices = dict(
    pol = device("nicos.devices.entangle.Motor",
        description = "Polarization",
        tangodevice = tango_s7 + "/pol",
        precision = 0.01,
    ),
    analyzer_shift = device("nicos.devices.entangle.NamedDigitalOutput",
        description = "Analyzer shift",
        tangodevice = tango_dio + "/analyzershift",
        mapping = {
            "in": 1,
            "out": 0,
        },
    ),
    pflipper = device("nicos_mlz.jcns.devices.polarizer.DOFlipper",
        description = "Polarizer flipper",
        tangodevice = tango_dio + "/pflipper",
        mapping = {
            "up": 0,
            "down": 1,
        },
        powersupplies = ["pow4curr1", "pow4curr2"],
    ),
    # aflipper (3HE) has inverted up/down mapping
#    aflipper = device("nicos_mlz.maria.devices.pyro4.NamedDigitalOutput",
#        description = "Pyro4 Device",
#        pyro4device = "PYRO:he3.cell@3he.maria.frm2:50555",
#        hmackey = "iamverysecret",
#        mapping = {
#            "down": 0,
#            "up": 1,
#        }
#    ),
    pow4curr1 = device("nicos_mlz.maria.devices.powersupply."
        "ReadOnlyPowerSupply",
        description = "Power supply 4 current control ch 1",
        tangodevice = tango_ps + "/pow4curr1",
        setpoint = 0.6,
        unit = 'A',
    ),
    pow4curr2 = device("nicos.devices.entangle.PowerSupply",
        description = "Power supply 4 current control ch 2",
        tangodevice = tango_ps + "/pow4curr2",
        unit = 'A',
    ),
    pol_state = device("nicos.devices.generic.MultiSwitcher",
        description = "Guide field switcher",
        moveables = ["pflipper", "aflipper"],
        mapping = {
            "dd": ("down", "down"),
            "du": ("down", "up"),
            "ud": ("up", "down"),
            "uu": ("up", "up"),
        },
        precision = None,
        unit = ''
    ),
)
