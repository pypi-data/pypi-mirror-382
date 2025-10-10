description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'VTreff',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'nicos_mlz.maria.scan']

includes = []

devices = dict(
    VTreff = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'VTREFF',
        responsible = 'Egor Vehzlev <e.vehzlev@fz-juelich.de>',
        website = 'http://www.mlz-garching.de',
        operators = [
            'Jülich Centre for Neutron Science (JCNS)',
            'Technische Universität München (TUM)',
        ],
    ),
    StandardSample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
        visibility = (),
    ),
    Sample = device('nicos_virt_mlz.treff.devices.MirrorSample',
        description = 'The currently used mirror sample',
        alignerrors = {
            'sample_y': 2,
            'omega': 0.01,
            'detarm': 0.1,
            'chi': 0.5,
        },
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Experiment object',
        dataroot = 'data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o750,
            disableFileMode = 0o440,
        ),
        mailserver='mailhost.frm2.tum.de',
        mailsender='c.felder@fz-juelich.de',
        sendmail = True,
        zipdata = True,
        sample = 'Sample',
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
