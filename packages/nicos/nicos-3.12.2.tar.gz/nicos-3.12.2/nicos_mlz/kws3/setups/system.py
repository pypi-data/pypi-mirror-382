description = 'system setup'
group = 'lowlevel'
display_order = 80

sysconfig = dict(
    cache = 'localhost',
    instrument = 'KWS3',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    KWS3 = device('nicos.devices.instrument.Instrument',
        description = 'KWS-3 instrument',
        instrument = 'KWS-3',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-28',
        responsible = 'V. Pipich <v.pipich@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/kws-3',
    ),
    Sample = device('nicos_mlz.kws1.devices.sample.KWSSample',
        description = 'Sample object',
        apname = 'sam_ap',
    ),
    Exp = device('nicos_mlz.kws3.devices.experiment.KWS3Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        mailsender = 'kws3@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        serviceexp = 'maintenance',
        sample = 'Sample',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o400,
            owner = 'jcns',
            group = 'mlzinstr'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
