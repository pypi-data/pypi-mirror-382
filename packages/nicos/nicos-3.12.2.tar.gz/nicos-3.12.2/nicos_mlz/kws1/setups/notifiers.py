description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'kws1@frm2.tum.de',
        copies = [
            ('g.brandl@fz-juelich.de', 'all'),
            ('a.feoktystov@fz-juelich.de', 'all'),
            ('h.frielinghaus@fz-juelich.de', 'all'),
            ('z.mahhouti@fz-juelich.de', 'all'),
        ],
        subject = '[KWS-1]',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
