description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'The notifier to send emails',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'resi@frm2.tum.de',
        copies = [('bjoern.pedersen@frm2.tum.de', 'all')],
        subject = 'RESI',
    ),

    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2.tum.de',
    #     receivers = [],
    #     subject = 'RESI',
    # ),
)
