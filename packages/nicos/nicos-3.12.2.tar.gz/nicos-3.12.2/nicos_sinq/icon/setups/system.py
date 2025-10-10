description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'ICON',
    experiment = 'Exp',
    datasinks = [
        'conssink',
        'dmnsink',
        'livesink',
        'asciisink',
    ],
    notifiers = ['email'],
)

includes = ['shutters']

display_order = 100

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos.commands.imaging', 'nicos_sinq.commands.hmcommands',
    'nicos_sinq.commands.epicscommands', 'nicos_sinq.icon.commands.iconcommands'
]

includes = ['notifiers']

devices = dict(
    ICON = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ ICON',
        responsible = 'Anders Kaestner <anders.kaestner@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        doi = 'http://dx.doi.org/10.1016/j.nima.2011.08.022',
        website = 'https://www.psi.ch/sinq/ICON/',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'The defaultsample',
    ),
    Exp = device('nicos_sinq.devices.experiment.TomoSinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        serviceexp = 'Service',
        sample = 'Sample',
        elog = False,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    emergency = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Emergency stop indicator',
        readpv = 'SQ:ICON:b2io1:EmergencyRBV',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    asciisink = device('nicos.devices.datasinks.AsciiScanfileSink',
        filenametemplate = ['icon%(year)sn%(scancounter)06d.dat']
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
    img_index = device('nicos.devices.generic.manual.ManualMove',
        description = 'Keeps the index of the last measured image',
        unit = '',
        abslimits = (0, 1e9),
        visibility = (),
    ),
)
