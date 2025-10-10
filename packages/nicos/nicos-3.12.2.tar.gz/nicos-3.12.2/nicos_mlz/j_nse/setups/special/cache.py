description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        # cannot use /data until main instrument control is switched to NICOS
        storepath = '/home/jcns/nicos-cache',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = '',
    ),
)
