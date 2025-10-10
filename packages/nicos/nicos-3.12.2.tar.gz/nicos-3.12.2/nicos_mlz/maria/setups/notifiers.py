description = 'Email and SMS notifier'
group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    mailer = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'maria@frm2.tum.de',
        copies = [
            ('a.koutsioumpas@fz-juelich.de', 'all'),
            ('c.felder@fz-juelich.de', 'important'),
        ],
        subject = '[NICOS] MARIA',
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
