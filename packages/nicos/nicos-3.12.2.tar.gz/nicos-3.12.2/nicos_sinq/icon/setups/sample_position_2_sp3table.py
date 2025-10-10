description = 'SP3 table mounted at sample position 2.'

excludes = ['sample_position_3']
includes = ['sample_position_2']

display_order = 41

devices = dict(
    sp3_ry = device('nicos.devices.epics.pyepics.motor.HomingProtectedEpicsMotor',
        description = 'Sample Position 3, Rotation Y',
        motorpv = 'SQ:ICON:board6:SP3RY',
        errormsgpv = 'SQ:ICON:board6:SP3RY-MsgTxt',
        precision = 0.01,
    ),
    sp3_rz = device('nicos.devices.epics.pyepics.motor.HomingProtectedEpicsMotor',
        description = 'Sample Position 3, Rotation Z',
        motorpv = 'SQ:ICON:board6:SP3RZ',
        errormsgpv = 'SQ:ICON:board6:SP3RZ-MsgTxt',
        precision = 0.01,
    ),
)
