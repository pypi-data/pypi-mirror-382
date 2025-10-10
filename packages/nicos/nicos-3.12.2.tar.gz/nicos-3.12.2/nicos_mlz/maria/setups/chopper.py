description = "Chopper setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_s7 = tango_base + "/FZJS7"

devices = dict(
    chopper_lift = device("nicos.devices.entangle.Motor",
        description = "Chopper",
        tangodevice = tango_s7 + "/chopper",
        precision = 0.01,
    ),
)
