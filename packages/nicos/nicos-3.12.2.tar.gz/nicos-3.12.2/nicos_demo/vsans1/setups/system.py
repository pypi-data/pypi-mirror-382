description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.cache_host'),
    instrument = 'VSANS1',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

includes = ['notifiers', 'reactor', 'nl4a']

devices = dict(
    Sample = device('nicos_mlz.sans1.devices.sample.Sample',
        description = 'sample',
    ),
    VSANS1 = device('nicos.devices.instrument.Instrument',
        description = 'SANS1 instrument',
        instrument = 'SANS-1',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-32',
        responsible = 'Dr. Andre Heinemann <Andre.Heinemann@hzg.de>',
        operators = ['German Engineering Materials Science Centre (GEMS)',
                     'Technische Universität München (TUM)',
                    ],
        website = 'http://www.mlz-garching.de/sans-1',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment',
        dataroot = configdata('config_data.dataroot'),
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = configdata('config_data.dataroot'),
        minfree = 0.5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = configdata('config_data.logging_path'),
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
