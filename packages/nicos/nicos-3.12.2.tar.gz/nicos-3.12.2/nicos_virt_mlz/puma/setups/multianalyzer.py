description = 'PUMA multianalyzer device'

group = 'lowlevel'

includes = ['aliases']

vis = ('devlist', 'namespace', 'metadata')

devices = dict(
    man = device('nicos_mlz.puma.devices.MultiAnalyzer',
        description = 'PUMA multi analyzer',
        translations = ['ta1', 'ta2', 'ta3', 'ta4', 'ta5', 'ta6', 'ta7', 'ta8',
                        'ta9', 'ta10', 'ta11'],
        rotations = ['ra1', 'ra2', 'ra3', 'ra4', 'ra5', 'ra6', 'ra7', 'ra8',
                     'ra9', 'ra10', 'ra11'],
    ),
    muslit_t = device('nicos.devices.generic.Axis',
        description = 'translation multianalyzer slit',
        motor = device('nicos.devices.generic.virtual.VirtualMotor',
            abslimits = (471, 565),
            unit = 'mm',
        ),
        precision = 1,
        fmtstr = '%.2f',
    ),
)

for i in range(1, 12):
    devices['ta%d' % i] = device('nicos.devices.generic.Axis',
        description = 'Translation crystal %d multianalyzer' % i,
        motor = device('nicos_mlz.puma.devices.VirtualReferenceMotor',
            abslimits = (-125.1, 125.1),
            userlimits = (-125, 125),
            unit = 'mm',
            refpos = 0.,
            fmtstr = '%.3f',
            speed = 5.0,
        ),
        precision = 0.01,
        visibility = vis,
    )
    devices['ra%d' % i] = device('nicos.devices.generic.Axis',
        description = 'Rotation crystal %d multianalyzer' % i,
        motor = device('nicos_mlz.puma.devices.VirtualReferenceMotor',
            abslimits = (-60.1, 0.5),
            userlimits = (-60.05, 0.5),
            unit = 'deg',
            refpos = 0.1,
            fmtstr = '%.3f',
            speed = 1.0,
        ),
        precision = 0.01,
        visibility = vis,
    )

alias_config = {
    'theta': {'ra6': 200},
}
