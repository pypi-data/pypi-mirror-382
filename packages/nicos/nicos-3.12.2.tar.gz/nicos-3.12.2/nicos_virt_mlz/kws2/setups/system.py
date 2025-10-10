description = 'system setup'
group = 'lowlevel'
display_order = 80

sysconfig = dict(
    cache = 'localhost',
    instrument = 'KWS2',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    KWS2 = device('nicos.devices.instrument.Instrument',
        description = 'KWS-2 instrument',
        instrument = 'KWS-2',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-27',
        responsible = 'A. Radulescu <a.radulescu@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/kws-2',
    ),
    Sample = device('nicos_mlz.kws1.devices.sample.KWSSample',
        description = 'Sample object',
    ),
    Exp = device('nicos_mlz.kws1.devices.experiment.KWSExperiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        mailsender = 'vkws@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        serviceexp = 'maintenance',
        sample = 'Sample',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
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

extended = dict(
    representative = 'Sample',
)
