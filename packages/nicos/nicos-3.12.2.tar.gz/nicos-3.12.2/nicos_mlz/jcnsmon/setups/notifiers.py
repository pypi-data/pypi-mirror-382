description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'jcns@frm2.tum.de',
        copies = [('g.brandl@fz-juelich.de', 'all'),
                  ('c.felder@fz-juelich.de', 'all')],
        subject = 'JCNSmon',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['01782979497'],
    ),
)
