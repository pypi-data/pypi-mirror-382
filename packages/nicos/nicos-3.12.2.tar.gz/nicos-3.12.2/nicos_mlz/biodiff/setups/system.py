description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'biodiff',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard', 'nicos_mlz.biodiff.commands']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Sample under investigation'
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Experiment device',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o400,
            owner = 'jcns',
            group = 'mlzinstr'
        ),
        mailsender = 'biodiff@frm2.tum.de',
        sendmail = True,
        zipdata = True,
        sample = 'Sample',
    ),
    biodiff = device('nicos.devices.instrument.Instrument',
        description = 'Single crystal DIFFractometer for BIOlogical macromolecules',
        instrument = "BIODIFF",
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-19',
        responsible = "Tobias Schrader <t.schrader@fz-juelich.de>",
        operators = [
            'Technische Universität München (TUM)',
            'Jülich Centre for Neutron Science (JCNS)',
        ],
        website = 'http://www.mlz-garching.de/biodiff',
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
