description = 'system setup for DNS '

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'dns',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Default Sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'DNS Experiment',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o400,
            owner = 'jcns',
            group = 'mlzinstr'
        ),
        sample = 'Sample',
    ),
    dns = device('nicos.devices.instrument.Instrument',
        description = 'DNS Diffuse scattering neutron ' +
        'time of flight spectrometer',
        instrument = 'DNS',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-33',
        responsible = 'Yixi Su <y.su@fz-juelich.de>',
        website = 'http://www.mlz-garching.de/dns',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output format.',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device storing console output.',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Device storing deamon output.',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)

extended = dict(
    representative = 'Sample',
)
