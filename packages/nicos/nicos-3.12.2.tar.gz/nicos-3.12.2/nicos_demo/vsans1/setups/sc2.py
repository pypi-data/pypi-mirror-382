description = 'sample changer 2 devices'

group = 'optional'

includes = ['sample_changer', 'sample_table']

devices = dict(
    sc2_y = device('nicos.devices.generic.Axis',
        description = 'Sample Changer 1/2 Axis',
        pollinterval = 15,
        maxage = 60,
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        precision = 0.01,
        motor = 'sc2_ymot',
    ),
    sc2_ymot = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample Changer 1/2 Axis motor',
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        unit = 'mm',
        visibility = (),
    ),
    sc2 = device('nicos.devices.generic.MultiSwitcher',
        description = 'Sample Changer 2 Huber device',
        moveables = ['sc2_y', 'st1_z'],
        mapping = {
            11: [592.5, -32],
            10: [533.5, -32],
            9: [474.5, -32],
            8: [415.5, -32],
            7: [356.5, -32],
            6: [297.5, -32],
            5: [238.5, -32],
            4: [179.5, -32],
            3: [120.5, -32],
            2: [61.5, -32],
            1: [2.5, -32],
            22: [592.5, 27],
            21: [533.5, 27],
            20: [474.5, 27],
            19: [415.5, 27],
            18: [356.5, 27],
            17: [297.5, 27],
            16: [238.5, 27],
            15: [179.5, 27],
            14: [120.5, 27],
            13: [61.5, 27],
            12: [2.5, 27],
        },
        fallback = 0,
        fmtstr = '%d',
        precision = [0.05, 0.05],
        blockingmove = False,
    ),
)

alias_config = {
    'SampleChanger': {'sc2': 100},
}
