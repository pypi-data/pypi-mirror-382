description = 'Devices for the Pfeiffer vakuum measuring device'

pvprefix = 'SQ:FOCUS:PFIFF:'

devices = dict(
    pf_flightpath = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Vakuum value for flightpath',
        readpv = pvprefix + 'Flightpath',
        visibility = ()
    ),
    pf_antitrumpet = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Vakuum value for antitrumpet',
        readpv = pvprefix + 'Antitrumpet',
        visibility = ()
    ),
    pf_sample = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Vakuum value for sample chamber',
        readpv = pvprefix + 'SampleChamber',
        visibility = ()
    ),
    pf_bef = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Vakuum value for BE filter',
        readpv = pvprefix + 'BeFilter',
        visibility = ()
    ),
    pfeiffer = device('nicos_sinq.focus.devices.pfeiffer.PfeifferReadable',
        description = 'Master device for pfeiffer',
        sensors = ['pf_flightpath', 'pf_antitrumpet', 'pf_sample', 'pf_bef'],
        switchstates = {
            'enable': 1,
            'disable': 0
        },
        switchpvs = {
            'read': pvprefix + 'SWITCH_RBV',
            'write': pvprefix + 'SWITCH'
        },
        unit = 'mbar'
    ),
)
