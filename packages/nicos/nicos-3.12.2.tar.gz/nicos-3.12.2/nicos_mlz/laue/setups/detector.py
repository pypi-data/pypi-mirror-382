description = 'PSL 2-D detector'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['tiff', 'raw', 'sraw', 'live'],
)

devices = dict(
    image = device('nicos_mlz.laue.devices.psldetector.PSLDetector',
        description = 'PSL detector image',
        address = 'lauedet.laue.frm2.tum.de',
        port = 50000,
    ),
    live = device('nicos.devices.datasinks.LiveViewSink',
        description = 'live sink',
    ),
    raw = device('nicos.devices.datasinks.RawImageSink',
        description = 'raw sink',
        filenametemplate = ['s%(pointcounter)08d.raw'],
        subdir = '',
    ),
    sraw = device('nicos.devices.datasinks.SingleRawImageSink',
        description = 'single raw sink',
        filenametemplate = ['s%(pointcounter)08d.sraw'],
        subdir = '',
    ),
    tiff = device('nicos_mlz.laue.devices.lauetiff.TIFFLaueSink',
        description = 'tiff sink',
        filenametemplate = ['%(pointcounter)08d.tif'],
        subdir = '',
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer',
        visibility = (),
    ),
    det1 = device('nicos_mlz.laue.devices.psldetector.SyncedDetector',
        description = 'PSL detector',
        timers = ['timer'],
        images = ['image'],
    ),
)
