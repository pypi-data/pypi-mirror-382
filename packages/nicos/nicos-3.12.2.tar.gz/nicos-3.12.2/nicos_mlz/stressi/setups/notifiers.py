description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'stressi@frm2.tum.de',
        copies = [
            ('michael.hofmann@frm2.tum.de', 'all'),
            ('weimin.gan@hzg.de', 'all'),
            ('joana.kornmeier@frm2.tum.de', 'important'),
        ],
        subject = 'STRESS-SPEC',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    hvemail = device('nicos.devices.notifiers.Mailer',
        sender = 'stressi@frm2.tum.de',
        copies = [
            ('michael.hofmann@frm2.tum.de', 'all'),
            ('weimin.gan@hzg.de', 'all'),
            ('karl.zeitelhack@frm2.tum.de', 'important'),
            ('ilario.defendi@frm2.tum.de', 'important'),
            ('joana.kornmeier@frm2.tum.de', 'important'),
        ],
        subject = 'STRESS-SPEC',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        subject = 'STRESS-SPEC',
        receivers = [],
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'stressi@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'STRESS-SPEC log space runs full',
    ),
)
