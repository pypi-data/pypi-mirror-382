description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.cache_host'),
    instrument = 'ErWIN',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    ErWIN = device('nicos.devices.instrument.Instrument',
        description = 'demo instrument',
        instrument = 'V-ErWIN',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        website = 'https://www.nicos-controls.org',
        operators = ['NICOS developer team'],
        facility = 'NICOS demo instruments',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = configdata('config_data.dataroot'),
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = configdata('config_data.dataroot'),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = configdata('config_data.logging_path'),
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
    else:
        NewExperiment(0, 'NICOS demo experiment',
                      localcontact='H. Maier-Leibnitz <heinz.maier-leibnitz@frm2.tum.de>')
        AddUser('Nico Suser', 'nico.suser@frm2.tum.de>', 'MLZ')
        NewSample('Gd3CdB7')
'''
