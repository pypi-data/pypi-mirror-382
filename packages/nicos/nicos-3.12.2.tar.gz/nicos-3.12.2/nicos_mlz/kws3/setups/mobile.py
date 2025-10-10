description = 'Mobile Sample devices'
group = 'optional'
display_order = 40

excludes = ['virtual_sample']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    sam_rot = device('nicos.devices.entangle.Motor',
        description = 'rot-table inside vacuum chamber 10m',
        tangodevice = s7_motor + 'sam_rot',
        unit = 'deg',
        precision = 0.01,
    ),
    sam_phi = device('nicos.devices.entangle.Motor',
        description = 'tilt-table-phi in vacuum chamber 10m',
        tangodevice = s7_motor + 'sam_phi',
        unit = 'deg',
        precision = 0.01,
    ),
    sam_chi = device('nicos.devices.entangle.Motor',
        description = 'tilt-table-chi in vacuum chamber 10m',
        tangodevice = s7_motor + 'sam_chi',
        unit = 'deg',
        precision = 0.01,
    ),
)
