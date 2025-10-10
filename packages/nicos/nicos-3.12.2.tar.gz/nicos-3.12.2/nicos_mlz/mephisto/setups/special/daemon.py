description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [('guest', '', 'guest'),
                  ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                  ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin')],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'mephisto17.office.frm2.tum.de',
        authenticators = ['Auth'],
        loglevel = 'info',
    ),
)
