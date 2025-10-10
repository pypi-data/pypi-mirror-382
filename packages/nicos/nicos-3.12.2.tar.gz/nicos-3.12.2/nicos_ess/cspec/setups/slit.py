description = 'Sample slit'

group = 'lowlevel'

devices = dict(
    slits_u=device(
        'nicos.devices.generic.VirtualMotor',
        description='upper edge of sample slit',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-10, 43),
        visibility=(),
    ),
    slits_b=device(
        'nicos.devices.generic.VirtualMotor',
        description='bottom edge of sample slit',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-43, 10),
        visibility=(),
    ),
    slits_l=device(
        'nicos.devices.generic.VirtualMotor',
        description='left edge of sample slit',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-26, 10),
        visibility=(),
    ),
    slits_r=device(
        'nicos.devices.generic.VirtualMotor',
        description='right edge of sample slit',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-10, 26),
        visibility=(),
    ),
    slits=device(
        'nicos.devices.generic.Slit',
        description='sample slit 4 blades',
        left='slits_l',
        right='slits_r',
        bottom='slits_b',
        top='slits_u',
        opmode='centered',
    ),
)
