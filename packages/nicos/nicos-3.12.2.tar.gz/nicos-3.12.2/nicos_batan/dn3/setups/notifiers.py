description = 'Email and SMS notifier examples'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'dn3@batan.go.id',
        copies = [
            ('rifai@batan.go.id', 'all'),   # gets all messages
            ('andon@batan.go.id', 'important'), # gets only important messages
        ],
        mailserver = '',  # please add it later !
        subject = 'NICOS DN3',
    ),
)
