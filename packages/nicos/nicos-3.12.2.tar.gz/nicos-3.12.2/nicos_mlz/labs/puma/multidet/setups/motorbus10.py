description = 'Motor bus 10'

group = 'lowlevel'

tango_base = 'tango://pumadma.puma.frm2.tum.de:10000/puma/'

devices = dict(
    motorbus10 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus10/bio',
       visibility = (),
    ),
)
