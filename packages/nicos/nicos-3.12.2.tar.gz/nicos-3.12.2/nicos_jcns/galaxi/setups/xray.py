description = 'GALAXI x-ray beam alignment motors setup'
group = 'optional'

display_order = 7

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    roy = device('nicos.devices.entangle.MotorAxis',
        description = 'ROY axis.',
        tangodevice = s7_motor + 'roy',
        offset = 0,
        precision = 0.01,
        fmtstr = '%d',
        userlimits = (-50000, 50000),
    ),
    roz = device('nicos.devices.entangle.MotorAxis',
        description = 'ROZ axis.',
        tangodevice = s7_motor + 'roz',
        offset = 0,
        precision = 0.01,
        fmtstr = '%d',
        userlimits = (-300000, 300000),
    ),
    dofchi = device('nicos.devices.entangle.MotorAxis',
        description = 'DOFChi axis.',
        tangodevice = s7_motor + 'dofchi',
        offset = 0,
        precision = 0.01,
        userlimits = (-50, 50),
    ),
    dofom = device('nicos.devices.entangle.MotorAxis',
        description = 'DOFOm axis.',
        tangodevice = s7_motor + 'dofom',
        offset = 0,
        precision = 0.01,
        userlimits = (-100, 100),
    ),
    roby = device('nicos.devices.entangle.MotorAxis',
        description = 'ROBY axis.',
        tangodevice = s7_motor + 'roby',
        offset = 0,
        precision = 0.01,
    ),
    robz = device('nicos.devices.entangle.MotorAxis',
        description = 'ROBZ axis.',
        tangodevice = s7_motor + 'robz',
        offset = 0,
        precision = 0.01,
    ),
)
