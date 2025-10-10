description = "Collimation setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_s7 = tango_base + "/FZJS7"
tango_dio = tango_base + "/FZJDP_Digital"

atten_mapping = {"out": 0, "in": 1}

devices = dict(
    giref = device("nicos.devices.entangle.Motor",
        description = "Collimation/GISANS",
        tangodevice = tango_s7 + "/giref",
        precision = 0.01,
    ),
    # TODO: add info about attenuation factors, or at least about the relative
    #       attenuation of A, B, C
    atten_A = device("nicos.devices.entangle.NamedDigitalOutput",
        description = "Attenuator A",
        tangodevice = tango_dio + "/attenA",
        mapping = atten_mapping,
    ),
    atten_B = device("nicos.devices.entangle.NamedDigitalOutput",
        description = "Attenuator B",
        tangodevice = tango_dio + "/attenB",
        mapping = atten_mapping,
    ),
    atten_C = device("nicos.devices.entangle.NamedDigitalOutput",
        description = "Attenuator C",
        tangodevice = tango_dio + "/attenC",
        mapping = atten_mapping,
    ),
)
