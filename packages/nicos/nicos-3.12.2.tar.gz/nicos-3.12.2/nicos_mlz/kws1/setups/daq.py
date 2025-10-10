description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 25

includes = ['counter', 'gedet']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat', 'binaryformat', 'LiveViewSink'],
)

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    det_ext_rt = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Switch for external-start realtime mode',
        tangodevice = tango_base + 'sps/rtswitch',
        mapping = {'off': 0,
                   'on': 1},
    ),
    det_img = device('nicos_mlz.kws1.devices.daq.GEImageChannel',
        description = 'Image for the large KWS detector',
        tangodevice = 'tango://phys.kws1.frm2:10000/kws1/ge/det',
        timer = 'timer',
        highvoltage = 'gedet_HV',
        fmtstr = '%d (%.1f cps)',
        rebin8x8 = True,
    ),
    det_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Current detector mode',
        device = 'det_img',
        parameter = 'mode',
    ),
    kwsformat = device('nicos_mlz.kws1.devices.kwsfileformat.KWSFileSink',
        detectors = ['det'],
        transpose = True,
    ),
    yamlformat = device('nicos_mlz.kws1.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    binaryformat = device('nicos_mlz.kws1.devices.yamlformat.BinaryArraySink',
        detectors = ['det'],
    ),
    det_roi = device('nicos_mlz.kws1.devices.daq.ROIRateChannel',
        description = 'Counts inside beamstop',
        bs_x = 'beamstop_x',
        bs_y = 'beamstop_y',
        timer = 'timer',
        xscale = (0.125, 67.0),
        yscale = (0.125, 88.0),
        size = (6, 5),
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2', 'mon3', 'selctr'],
        images = ['det_img'],
        counters = ['det_roi'],
        others = [],
        postprocess = [('det_roi', 'det_img')],
        shutter = 'shutter',
        liveinterval = 2.0,
    ),
)

extended = dict(
    poller_cache_reader = ['shutter', 'gedet_HV', 'beamstop_x', 'beamstop_y'],
    representative = 'det_img',
)
