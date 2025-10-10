description = 'Laser distance measurement device in AMOR'

group = 'lowlevel'

devices = dict(
    dimetix = device('nicos_sinq.amor.devices.dimetix.EpicsDimetix',
        description = 'Laser distance measurement device',
        readpv = 'SQ:AMOR:DIMETIX:DIST',
        offset = -238,
        visibility = ()
    ),
    xlz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Counter z position distance laser motor',
        motorpv = 'SQ:AMOR:mota:xlz',
        visibility = (),
    ),
    laser_positioner = device('nicos.devices.generic.Switcher',
        description = 'Position laser to read components',
        moveable = 'xlz',
        mapping = {
            'park': -0.1,
            'analyser': -24.0,
            'detector': 0.0,
            'polariser': -88.0,
            'sample': -52.0,
            'slit2': -73.0,
            'slit3': -63.0,
            'slit4': -34.0,
            'selene': -116.0,
        },
        fallback = '<undefined>',
        precision = 0,
        visibility = ()
    ),
)
