description = 'system setup only'

group = 'lowlevel'

sysconfig = dict(
    cache = 'resictrl.resi.frm2.tum.de',
    instrument = 'resiInstrument',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    Exp = device('nicos_mlz.resi.devices.experiment.ResiExperiment',
        description = 'The currently running experiment',
        sample = 'Sample',
        dataroot = '/data/data6/',
    ),
    resiInstrument = device('nicos.devices.instrument.Instrument',
        description = 'Thermal neutron single crystal diffractometer',
        instrument = 'RESI',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-23',
        responsible = 'B. Pedersen <bjoern.pedersen@frm2.tum.de>',
        operators = ['Ludwig-Maximilians-Universität München (LMU)'],
        website = 'http://www.mlz-garching.de/resi',
    ),
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'The sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
)
