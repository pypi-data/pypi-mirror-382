description = 'Motor bus 2'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2.tum.de:10000/puma/'

devices = dict(
    motorbus2 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus2/bio',
       visibility = (),
    ),
)
