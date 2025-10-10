description = 'system setup'

sysconfig = dict(
    cache = 'tequila.pgaa.frm2.tum.de',
    instrument = 'PGAA',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.pgaa.commands']

group = 'lowlevel'

includes = ['notifiers']

devices = dict(
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'The sample',
    ),
    PGAA = device('nicos.devices.instrument.Instrument',
        description = 'Prompt gamma and in-beam neutron activation analysis '
                      'facility',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-46',
        responsible = 'Dr. Zsolt Revay <zsolt.revay@frm2.tum.de>',
        operators = ['Universität zu Köln'],
        website = 'http://www.mlz-garching.de/pgaa',
        instrument = 'pgaa',
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'The currently running experiment',
        dataroot = '/data/',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos_mlz.pgaa.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing log files',
        path = '/control/log',
        minfree = .5,
    ),
)
