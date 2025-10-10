description = 'sample table'

group = 'lowlevel'

devices = dict(
    x=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='X translation of the sample table',
        fmtstr="%7.2f",
        abslimits=(-20.0, 20.),
        speed=2,
        unit='mm',
    ),
    y=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='Y translation of the sample table',
        fmtstr="%7.2f",
        abslimits=(-20.0, 20.),
        speed=2,
        unit='mm',
    ),
    z=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='Z translation of the sample table',
        fmtstr="%7.2f",
        abslimits=(-14.8, 50.),
        speed=1,
        unit='mm',
    ),
    chi=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='Chi rotation of the sample goniometer',
        fmtstr="%7.2f",
        abslimits=(-20.0, 20.),
        speed=1,
        unit='deg',
    ),
    psi=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='Psi rotation of the sample goniometer',
        fmtstr="%7.2f",
        abslimits=(-20.0, 20.),
        speed=1,
        unit='deg',
    ),
    phi=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='Phi rotation of the sample table',
        fmtstr="%7.2f",
        abslimits=(-100.0, 100.),
        speed=1,
        unit='deg',
    ),
)
