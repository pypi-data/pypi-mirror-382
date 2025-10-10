description = 'Kepco power supply'

pv_root = 'utg-kepco-001:'

devices = dict(
    IDN_kepco=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The hardware Identification',
        readpv='{}IDN_rbv'.format(pv_root),
    ),
    V_kepco=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='The Voltage',
        readpv='{}MeasVolt'.format(pv_root),
        writepv='{}Volt'.format(pv_root),
        targetpv='{}Volt_rbv'.format(pv_root),
    ),
    Remote_kepco=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Setting remote mode on/off',
        readpv='{}Remote_rbv'.format(pv_root),
        writepv='{}Remote'.format(pv_root),
    ),
    Output_kepco=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Setting output on/off',
        readpv='{}Output_rbv'.format(pv_root),
        writepv='{}Output'.format(pv_root),
    ),
)
