description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'nectar@frm2.tum.de',
        copies = [
            ('adrian.losko@frm2.tum.de', 'all'),
            ('michael.schulz@frm2.tum.de', 'important'),
        ],
        subject = '[NECTAR]',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    warning = device('nicos.devices.notifiers.Mailer',
        sender = 'nectar@frm2.tum.de',
        copies = [
            ('adrian.losko@frm2.tum.de', 'all'),
            ('michael.schulz@frm2.tum.de', 'important'),
        ],
        subject = '[NECTAR]',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
        subject = '[NECTAR]',
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'nectar@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'NECTAR log space runs full',
    ),
)
