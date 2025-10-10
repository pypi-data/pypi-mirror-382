description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'HRPT',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'nxsink', 'livesink', 'quiecksink'],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands', 'nicos_sinq.commands.epicscommands'
]

devices = dict(
    HRPT = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ HRPT',
        responsible = 'Vladimir Pomjakushin <vladimir.pomjakushin@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/hrpt/',
    ),
    Sample = device('nicos_sinq.devices.sample.PowderSample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        serviceexp = 'Service',
        sample = 'Sample',
        forcescandata = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    nxsink = device('nicos.nexus.NexusSink',
        description = "Sink for NeXus file writer",
        filenametemplate = ['hrpt%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.hrpt.nexus.nexus_templates.HRPTTemplateProvider',
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile notifications'
    ),
)
"""
    KafkaForwarder=device('nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description="Monitors and controls forward-epics-to-kafka",
        statustopic="HRPT_forwarderStatus",
        brokers=configdata('config.KAFKA_BROKERS'),
    ),

    HistogramDataSink=device('nicos_ess.devices.datasinks.imagesink.kafka.ImageKafkaDataSink',
        brokers=configdata('config.KAFKA_BROKERS'),
        channeltostream={
            'area_detector': ('HRPT_bananaDetector', 'linear')
        },
    ),

    NexusDataSink=device('nicos_sinq.devices.datasinks.SinqNexusFileSink',
        description="Sink for NeXus file writer (kafka-to-nexus)",
        brokers=configdata('config.KAFKA_BROKERS'),
        filenametemplate=['hrpt%(year)sn%(pointcounter)06d.hdf'],
        cmdtopic="HRPT_filewriterCommands",
        status_provider='NexusFileWriter',
        templatesmodule='nicos_sinq.hrpt.nexus.nexus_templates',
        templatename='hrpt_default'
    ),

    NexusFileWriter=device('nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description="Status for nexus file writing",
        brokers=configdata('config.KAFKA_BROKERS'),
        statustopic="HRPT_filewriterStatus",
    ),
"""
