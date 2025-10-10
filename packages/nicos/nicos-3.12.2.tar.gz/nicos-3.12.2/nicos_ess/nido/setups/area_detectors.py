description = 'The area detector for NIDO'

KAFKA_BROKERS = ['10.102.80.32:8093']

devices = dict(
    hama_kafka_plugin=device(
        'nicos_ess.devices.epics.area_detector.ADKafkaPlugin',
        description=
        'The configuration of the Kafka plugin for the Hama camera.',
        kafkapv='Hama:Kfk1:',
        brokerpv='KafkaBrokerAddress_RBV',
        topicpv='KafkaTopic_RBV',
        sourcepv='SourceName_RBV',
        visibility=(),
    ),
    hama_camera=device(
        'nicos_ess.devices.epics.area_detector.AreaDetector',
        description='The light tomography Hama camera.',
        pv_root='Hama:cam1:',
        ad_kafka_plugin='hama_kafka_plugin',
        image_topic='nido_camera',
        unit='images',
        brokers=KAFKA_BROKERS,
        pollinterval=None,
        pva=True,
        monitor=True,
    ),
    hama_image_type=device(
        'nicos_ess.devices.epics.area_detector.ImageType',
        description="Image type for the tomography setup.",
    ),
    area_detector_collector=device(
        'nicos_ess.devices.epics.area_detector.AreaDetectorCollector',
        description='Area detector collector',
        images=['hama_camera'],
        liveinterval=1,
        pollinterval=1,
        unit='',
    ),
)

startupcode = '''
SetDetectors(area_detector_collector)
'''
