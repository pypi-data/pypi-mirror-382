description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/jnse',
        keyfilters = ['magb*.*', 'cooling.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.j-nse.frm2',
        forwarders = ['GlobalCache'],
    ),
)
