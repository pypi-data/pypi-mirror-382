description = 'setup for the poller'

group = 'special'

sysconfig = dict(
    cache = 'resictrl.resi.frm2.tum.de',
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        loglevel = 'info',
        autosetup = True,
        alwayspoll = [
            'ls340', 'io', 'reactor', 'ubahn', 'outerworld', 'detector'
        ],
        neverpoll = ['base', 'system', 'resi'],
        blacklist = [],
    ),
)
