description = 'Slit set 2'

group = 'optional'

devices = dict(
    slits_2_u=device(
        'nicos.devices.generic.VirtualMotor',
        description='Upper edge of slit set',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-10, 43),
        visibility=(),
    ),
    slits_2_b=device(
        'nicos.devices.generic.VirtualMotor',
        description='Bottom edge of slit set',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-43, 10),
        visibility=(),
    ),
    slits_2_l=device(
        'nicos.devices.generic.VirtualMotor',
        description='Left edge of slit set',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-26, 10),
        visibility=(),
    ),
    slits_2_r=device(
        'nicos.devices.generic.VirtualMotor',
        description='Right edge of slit set',
        fmtstr='%.2f',
        unit='mm',
        speed=0.5,
        abslimits=(-10, 26),
        visibility=(),
    ),
    slits_2=device(
        'nicos.devices.generic.Slit',
        description='Slit set with 4 blades',
        left='slits_2_l',
        right='slits_2_r',
        bottom='slits_2_b',
        top='slits_2_u',
        opmode='centered',
    ),
)
