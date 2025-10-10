description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'kws2@frm2.tum.de',
        copies = [
            ('g.brandl@fz-juelich.de', 'all'),
            ('a.radulescu@fz-juelich.de', 'all'),
            ('j.kang@fz-juelich.de', 'all'),
            ('t.kohnke@fz-juelich.de', 'all'),
            ('s.staringer@fz-juelich.de', 'all'),
        ],
        subject = '[KWS-2]',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
