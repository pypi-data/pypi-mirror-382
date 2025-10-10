description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 25

includes = ['virtual_gedet']

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat', 'binaryformat'],
)

devices = dict(
    det_ext_rt = device('nicos.devices.generic.ManualSwitch',
        description = 'Switch for external-start realtime mode',
        visibility = (),
        states = ['on', 'off', 1, 0],
    ),
    det_img = device('nicos_mlz.kws1.devices.daq.VirtualKWSImageChannel',
        description = 'Image for the large KWS detector',
        size = (144, 256),
    ),
    det_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Current detector mode',
        device = 'det_img',
        parameter = 'mode',
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer',
        fmtstr = '%.0f',
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 1 (before selector)',
        type = 'monitor',
        fmtstr = '%d',
    ),
    mon2 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 2 (after selector)',
        type = 'monitor',
        fmtstr = '%d',
    ),
    mon3 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 3 (in detector beamstop)',
        type = 'monitor',
        fmtstr = '%d',
    ),
    kwsformat = device('nicos_mlz.kws1.devices.kwsfileformat.KWSFileSink',
        transpose = False,
        detectors = ['det'],
    ),
    yamlformat = device('nicos_mlz.kws1.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
    ),
    binaryformat = device('nicos_mlz.kws1.devices.yamlformat.BinaryArraySink',
        detectors = ['det'],
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2', 'mon3'],
        images = ['det_img'],
        others = [],
        shutter = 'shutter',
    ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
    representative = 'det_img',
)
