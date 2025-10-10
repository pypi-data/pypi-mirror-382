description = 'The Lakeshore 155.'

pv_root = 'E04-SEE:LS155-001:'

devices = dict(
    ls155_mode=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='Current mode',
        readpv='{}FunctionMode-S'.format(pv_root),
    ),
    ls155_idn=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The device idn',
        readpv='{}IDN-R'.format(pv_root),
    ),
    ls155_amplitude_A=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='DC amplitude (current)',
        readpv='{}CurrAmp-R'.format(pv_root),
        writepv='{}CurrValue-S'.format(pv_root),
        abslimits=(-1e308, 1e308),
    ),
    ls155_amplitude_V=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='DC amplitude (current)',
        readpv='{}VoltAmp-R'.format(pv_root),
        writepv='{}VoltValue-S'.format(pv_root),
        abslimits=(-1e308, 1e308),
    ),
    ls155_output=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Outputting DC',
        readpv='{}OutputState-RBV'.format(pv_root),
        writepv='{}OutputState-S'.format(pv_root),
    ),
    ls155_shape=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Outputting DC',
        readpv='{}FunctionShape-RBV'.format(pv_root),
        writepv='{}FunctionShape-S'.format(pv_root),
    ),
)
