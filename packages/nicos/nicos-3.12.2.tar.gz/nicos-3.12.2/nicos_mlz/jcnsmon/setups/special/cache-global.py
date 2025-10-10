description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        storepath = '/data/cache',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = '0.0.0.0:14869',
        loglevel = 'info',
    ),
)
