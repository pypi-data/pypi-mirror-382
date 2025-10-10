description = 'Some kind of SKF chopper'

pv_root = 'LabS-Embla:Chop-Drv-0601:'

devices = dict(
    skf_drive_temp=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Drive temperature',
        readpv='{}DrvTmp_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_motor_temp=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Motor temperature',
        readpv='{}MtrTmp_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_pos_v13=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Position',
        readpv='{}PosV13_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_pos_v24=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Position',
        readpv='{}PosV24_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_pos_w13=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Position',
        readpv='{}PosW13_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_pos_w24=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Position',
        readpv='{}PosW24_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_pos_Z12=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Position',
        readpv='{}PosZ12_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_status=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The chopper status.',
        readpv='{}Chop_Stat'.format(pv_root),
        monitor=True,
    ),
    skf_control=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Used to start and stop the chopper.',
        readpv='{}Cmd'.format(pv_root),
        writepv='{}Cmd'.format(pv_root),
        requires={'level': 'user'},
    ),
    skf_speed=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The current speed.',
        requires={'level': 'user'},
        readpv='{}Spd_Stat'.format(pv_root),
        writepv='{}Spd_SP'.format(pv_root),
        abslimits=(0.0, 77),
        monitor=True,
    ),
)
