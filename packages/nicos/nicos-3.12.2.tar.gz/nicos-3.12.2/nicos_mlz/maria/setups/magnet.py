description = "Magnet Power supply setup"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"

devices = dict(
    magnet = device("nicos.devices.entangle.PowerSupply",
        description = "Magnet current control",
        tangodevice = tango_host + "/maria/bruker/magnet",
        precision = 0.05,
    ),
)
