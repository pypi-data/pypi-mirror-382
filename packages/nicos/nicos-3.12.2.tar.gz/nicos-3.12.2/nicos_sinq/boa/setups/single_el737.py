description = 'Neutron counter box'

group = 'lowlevel'

excludes = [
    'embl', 'embl_config', 'andor', 'andorccd', 'andorccd-l', 'fastcomtec', 'sim_ad'
]

pvprefix = 'SQ:BOA:counter'

devices = dict(
    timepreset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvprefix + '.TP',
        presetpv = pvprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvprefix + '.PR2',
        presetpv = pvprefix + '.PR2',
    ),
    monitorval = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for neutron beam',
        type = 'monitor',
        readpv = pvprefix + '.S2',
    ),
    protoncurr = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Monitor for proton current',
        type = 'monitor',
        readpv = pvprefix + '.S5',
    ),
    countval = device('nicos_sinq.devices.epics.detector'
        '.EpicsCounterPassiveChannel',
        description = 'Actual counts in single detector',
        type = 'monitor',
        readpv = pvprefix + '.S1',
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and manages '
        'monitors',
        startpv = pvprefix + '.CNT',
        pausepv = pvprefix + ':Pause',
        statuspv = pvprefix + ':Status',
        errormsgpv = pvprefix + ':MsgTxt',
        thresholdpv = pvprefix + ':Threshold',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = ['monitorval', 'protoncurr'],
        liveinterval = 20,
        saveintervals = [60]
    ),
)

startupcode = '''
SetDetectors(el737)
'''
