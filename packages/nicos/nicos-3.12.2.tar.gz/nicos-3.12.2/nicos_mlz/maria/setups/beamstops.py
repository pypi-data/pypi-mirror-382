description = "Beamstops setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_s7 = tango_base + "/FZJS7"

devices = dict(
    bsd = device("nicos.devices.entangle.Motor",
        description = "Beamstops/BSD",
        tangodevice = tango_s7 + "/bsd",
        precision = 0.01,
    ),
    bs1_rot = device("nicos.devices.entangle.Motor",
        description = "Beamstops/Ref_BSD 1 rotation",
        tangodevice = tango_s7 + "/bs1_rot",
        precision = 0.01,
    ),
    bs1_trans = device("nicos.devices.entangle.Motor",
        description = "Beamstops/Ref_BSD 1 translation",
        tangodevice = tango_s7 + "/bs1_trans",
        precision = 0.01,
    ),
    bs2_rot = device("nicos.devices.entangle.Motor",
        description = "Beamstops/Ref_BSD 2 rotation",
        tangodevice = tango_s7 + "/bs2_rot",
        precision = 0.01,
    ),
    bs2_trans = device("nicos.devices.entangle.Motor",
        description = "Beamstops/Ref_BSD 2 translation",
        tangodevice = tango_s7 + "/bs2_trans",
        precision = 0.01,
    ),
    sc = device("nicos.devices.entangle.Motor",
        description = "Sample changer",
        tangodevice = tango_s7 + "/sam_changer",
        precision = 0.01,
    )
)
