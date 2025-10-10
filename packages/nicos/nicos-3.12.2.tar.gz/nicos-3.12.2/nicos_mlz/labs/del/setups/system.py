description = 'system setup only'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'DEL',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        sample = 'Sample',
        dataroot = '/localdata/nicos',
        serviceexp = 'p0',
        mailsender = 'karl.zeitelhack@frm2.tum.de',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'currently used sample',
    ),
    DEL = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'DEL',
        responsible = 'Karl Zeitelhack <karl.zeitelhack@frm2.tum.de>',
        operators = ['Technische Universität München (TUM)'],
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'free space for data files',
        path = '/localdata/nicos',
        minfree = 10,
    ),
)
