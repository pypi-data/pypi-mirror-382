description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        description = 'On disk storage for Cache Server',
        storepath = '/data/cache',
        loglevel = 'info',
    ),

    Server = device('nicos.services.cache.server.CacheServer',
        description = 'Value caching server',
        db = 'DB',
        server = '',
        loglevel = 'info',
    ),
)
