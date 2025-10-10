description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Notifications via email',
        sender = 'sans1@frm2.tum.de',
        copies = [
            ('andreas.wilhelm@frm2.tum.de', 'important'),
            ('Andre.Heinemann@hzg.de', 'important'),
            ('sebastian.busch@hzg.de', 'important'),
            ('sebastian.muehlbauer@frm2.tum.de', 'important')
        ],
        mailserver = 'mailhost.frm2.tum.de',
        subject = 'SANS-1',
    ),
    warning = device('nicos.devices.notifiers.Mailer',
        description = 'warning notifcations via email',
        sender = 'sans1@frm2.tum.de',
        copies = [('andreas.wilhelm@frm2.tum.de', 'all')],
        subject = 'SANS-1 Warning',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    info = device('nicos.devices.notifiers.Mailer',
        description = 'info notifcations via email',
        sender = 'sans1@frm2.tum.de',
        copies = [('andreas.wilhelm@frm2.tum.de', 'all')],
        subject = 'SANS-1 Info',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2.tum.de',
    #     receivers = ['01719251564', '01782979497'],
    #     subject = 'SANS-1',
    # ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'sans1@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'SANS-1 log space runs full',
    ),
)
