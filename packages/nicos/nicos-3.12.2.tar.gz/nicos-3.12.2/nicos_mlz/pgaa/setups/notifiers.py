description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'pgaa@frm2.tum.de',
        copies = [
            ('zsolt.revay@frm2.tum.de', 'all'),
            ('revayzs@gmail.com', 'all'),
            ('christian.stieghorst@frm2.tum.de', 'all')
        ],
        mailserver = 'mailhost.frm2.tum.de',
        subject = 'PGAA',
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
        subject = 'PGAA',
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'pgaa@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'PGAA log space runs full',
    ),
)
