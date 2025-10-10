description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'ictrl@frm2.tum.de',
        copies = [('ictrl@frm2.tum.de', 'all'),   # gets all messages
                  ('ictrl@frm2.tum.de', 'important')], # gets only important messages
        subject = 'NICOS',
        mailserver = 'mailhost.frm2.tum.de',
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
