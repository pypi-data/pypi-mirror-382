description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'DiObSink'],
)

devices = dict(
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        description = 'Updates di/ob links',
    ),
)
