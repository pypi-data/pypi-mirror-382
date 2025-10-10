description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    experiment = None,
    instrument = None,
    datasinks = [],
    notifiers = [],
    cache = 'miractrl.mira.frm2.tum.de',
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        autosetup = True,
        alwayspoll = ['ubahn', 'outerworld', 'memograph'],
        neverpoll = ['gaussmeter'],
        loglevel = 'info',
        blacklist = ['psd_channel']
    ),
)
