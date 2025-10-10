description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer = device('nicos.devices.notifiers.Mailer',
        sender = 'se-trouble@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [],
        subject = 'SE',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
