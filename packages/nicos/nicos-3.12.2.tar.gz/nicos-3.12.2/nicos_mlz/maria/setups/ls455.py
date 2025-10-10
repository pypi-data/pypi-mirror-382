description = "Gauss meter setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"

devices = dict(
    field = device("nicos.devices.entangle.AnalogInput",
        description = "Lakeshore LS455, DSP Gauss Meter",
        tangodevice = tango_base + "/ls455/field",
    ),
)
