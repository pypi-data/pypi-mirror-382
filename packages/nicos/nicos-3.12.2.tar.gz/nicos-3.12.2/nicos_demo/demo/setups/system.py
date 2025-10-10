description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'demo',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    demo = device('nicos.devices.instrument.Instrument',
        description = 'demo instrument',
        instrument = 'DEMO',
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
        dataroot = 'data',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = None,
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = 'log',
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
        AddUser('Nico Suser', 'nico.suser@frm2.tum.de', 'Institute for Science')
        NewSample('Gd3CdB7')
'''

help_topics = {
    'NICOS demo': """
NICOS demo
==========

The NICOS demo is aimed to demonstrate the capabilities of the NICOS system.

There exist simulations for the following basic types of instruments:

#. TAS instrument (to use, please load the setup **tas**)
#. SANS instrument (to use, please load the setup **sans**)
""",
}
