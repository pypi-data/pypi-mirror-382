description = 'nGI G0 devices in the SINQ ICON.'

display_order = 20

group = 'lowlevel'

devices = dict(
    g0_tx = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'nGI Source Grating (G0) Translation X',
        motorpv = 'SQ:ICON:ngiG:g0tx',
        errormsgpv = 'SQ:ICON:ngiG:g0tx-MsgTxt',
        precision = 0.002,
    ),
    g0_rz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'nGI Source Grating (G0) Rotation Y',
        motorpv = 'SQ:ICON:ngiG:g0ry',
        errormsgpv = 'SQ:ICON:ngiG:g0ry-MsgTxt',
        precision = 0.01,
    )
)
