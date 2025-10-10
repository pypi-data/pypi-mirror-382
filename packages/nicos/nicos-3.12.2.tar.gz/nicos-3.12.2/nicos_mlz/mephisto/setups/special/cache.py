description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        storepath = '/localhome/data/cache',
        loglevel = 'info'
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = 'mephisto17.office.frm2.tum.de',
        loglevel = 'info'
    ),
)
