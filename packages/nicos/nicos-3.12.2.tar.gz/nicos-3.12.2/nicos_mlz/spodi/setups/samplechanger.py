description = 'Sample changer and rotation'

group = 'optional'

tangohost = 'tango://spodictrl.spodi.frm2.tum.de:10000/spodi/samplechanger/sc_'

devices = dict(
    samr = device('nicos.devices.entangle.NamedDigitalOutput',
        description = '(de-)activates the sample rotation',
        tangodevice = tangohost + 'rotation',
        mapping = dict(on=1, off=0),
    ),
    sams_e = device('nicos.devices.entangle.Sensor',
        description = 'Position of the sample change selection wheel',
        tangodevice = tangohost + 'selectencoder',
        unit = 'deg',
        visibility = (),
    ),
    sams_m = device('nicos.devices.entangle.Actuator',
        description = 'Motor position of the sample change selection wheel',
        tangodevice = tangohost + 'selectmotor',
        unit = 'deg',
        visibility = (),
    ),
    sams_a = device('nicos.devices.generic.Axis',
        description = 'Position of sample selection wheel',
        motor = 'sams_m',
        coder = 'sams_e',
        precision = 0.05,
        visibility = (),
    ),
    sams = device('nicos_mlz.spodi.devices.SampleChanger',
        description = 'Sample Changer drum',
        moveables = ['sams_a'],
        mapping = {
            'S1': [-3.04],
            'S2': [33.11],
            'S3': [68.8],
            'S4': [104.95],
            'S5': [140.93],
            'S6': [177.20],
            'S7': [212.91],
            'S8': [249.07],
            'S9': [285.11],
            'S10': [321.03],
        },
        fallback = '?',
        fmtstr = '%s',
        precision = [0.1],
        blockingmove = True,
        unit = '',
    ),
)
display_order = 60

alias_config = {
}
