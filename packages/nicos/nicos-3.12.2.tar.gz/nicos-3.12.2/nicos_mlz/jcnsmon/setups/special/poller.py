description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    # use only 'localhost' if the cache is really running on the same machine,
    # otherwise use the official computer name
    cache = 'localhost:14870'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = ['all_memographs'],
        neverpoll = [],  # setups that should not be polled even if loaded
        blacklist = [],  # DEVICES that should never be polled
        # (usually detectors or devices that have problems
        # with concurrent access from processes)
    ),
)
