description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 25

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat', 'binaryformat'],
)

includes = ['virtual_gedet']

devices = dict(
    kwsformat = device('nicos_mlz.kws2.devices.kwsfileformat.KWSFileSink',
        transpose = True,
        detectors = ['det'],
    ),
    yamlformat = device('nicos_mlz.kws2.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
    ),
    binaryformat = device('nicos_mlz.kws1.devices.yamlformat.BinaryArraySink',
        detectors = ['det'],
    ),
    det_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Current detector mode',
        device = 'det_img',
        parameter = 'mode',
    ),
    det_img_ge = device('nicos_mlz.kws1.devices.daq.VirtualKWSImageChannel',
        description = 'Image for the large KWS detector',
        size = (144, 256),
    ),
    det_img_jum = device('nicos_mlz.kws1.devices.daq.VirtualKWSImageChannel',
        description = 'Image for the small KWS detector',
        size = (256, 256),
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['det_img'],
        others = [],
        shutter = 'shutter',
        liveinterval = 2.0,
    ),
    det_img = device('nicos.devices.generic.DeviceAlias',
        alias = 'det_img_ge',
        devclass = 'nicos_mlz.kws1.devices.daq.VirtualKWSImageChannel',
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Measurement timer channel',
        fmtstr = '%.0f',
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 1 (before selector)',
        type = 'monitor',
        fmtstr = '%d',
        visibility = (),
    ),
    mon2 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 2 (after selector)',
        type = 'monitor',
        fmtstr = '%d',
        visibility = (),
    ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
    representative = 'det_img',
)
