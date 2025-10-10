description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'SPODI',
         ghosthost = 'ghost.mlz-garching.de',
         aliases = {
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://spodisrv.spodi.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=spodi,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=spodi,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'spodi': 'admin',
        },
    ),
    LDAPAuthBU = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://phaidra.admin.frm2.tum.de',
            'ldap://ariadne.admin.frm2.tum.de',
            'ldap://sarpedon.admin.frm2.tum.de',
            'ldap://minos.admin.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'spodi': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['UserDBAuth', 'LDAPAuth', 'LDAPAuthBU',],
        loglevel = 'info',
    ),
)
