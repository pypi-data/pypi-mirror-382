description = 'Virtual cryostat'

group = 'optional'

devices = dict(
    T=device(
        'nicos.devices.generic.DeviceAlias'
    ),
    Ts=device(
        'nicos.devices.generic.DeviceAlias'
    ),
    T_cryo=device(
        'nicos.devices.generic.VirtualRealTemperature',
        description='A virtual (but realistic) temperature controller',
        abslimits=(2, 1000),
        warnlimits=(0, 325),
        ramp=60,
        unit='K',
        jitter=0,
        precision=0.1,
        window=30.0,
        visibility=(),
    ),
    T_sample=device(
        'nicos.devices.generic.ReadonlyParamDevice',
        parameter='sample',
        device='T_cryo',
        description='Temperature of virtual sample',
        visibility=(),
    ),
)

alias_config = {
    'T': {
        'T_cryo': 100
    },
    'Ts': {
        'T_sample': 100
    },
}

startupcode = """
AddEnvironment(T, Ts)
"""
