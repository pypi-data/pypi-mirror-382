description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'utg',
    experiment = 'Exp',
    datasinks = ['conssink', 'livesink', 'dmnsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

includes = ['ubahn']

devices = dict(
    utg = device('nicos.devices.instrument.Instrument',
        description = 'UTG testing instrument',
        instrument = 'UTG',
        responsible = 'Martin Landesberger <martin.landesberger@utg.de>',
        website = 'https://www.utg.mw.tum.de/',
        operators = ['UTG', ],
        facility = 'TU Munich',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)

startupcode = '''
'''
