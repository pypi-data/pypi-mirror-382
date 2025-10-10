description = 'LoKI chopper'

pv_root = 'LOKI-ChpSy3:Chop-FOC-101:'

devices = dict(
    chopper_control_foc1=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Used to start and stop the chopper.',
        readpv='{}C_Execute'.format(pv_root),
        writepv='{}C_Execute'.format(pv_root),
        requires={'level': 'admin'},
        visibility=(),
    ),
    chopper_speed_foc1=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The current speed.',
        readpv='{}Spd_R'.format(pv_root),
        writepv='{}Spd_S'.format(pv_root),
        abslimits=(0.0, 14),
        monitor=True,
        precision=0.1,
    ),
    rotation_dir_foc1=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Rotation direction.',
        readpv='{}RotDir_R'.format(pv_root),
        monitor=True,
    ),
    in_phase_foc1=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='In phase.',
        readpv='{}InPhs_R'.format(pv_root),
        monitor=True,
    ),
    motor_temperature_foc1=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Motor temperature.',
        readpv='{}MtrTemp_R'.format(pv_root),
        monitor=True,
    ),
    drive_temperature_foc1=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Drive temperature.',
        readpv='{}DrvTemp_R'.format(pv_root),
        monitor=True,
    ),
    chopper_alarms_foc1=device(
        'nicos_ess.devices.epics.chopper.ChopperAlarms',
        description='Chopper alarms.',
        pv_root=pv_root,
        monitor=True,
    ),
)
