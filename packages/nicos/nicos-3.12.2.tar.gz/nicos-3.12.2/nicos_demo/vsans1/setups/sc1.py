description = 'sample changer 1 devices'

group = 'optional'

includes = ['sample_changer', 'sample_table']

devices = dict(
    sc1_y = device('nicos.devices.generic.Axis',
        description = 'Sample Changer 1 Axis',
        pollinterval = 15,
        maxage = 60,
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        precision = 0.01,
        motor = 'sc1_ymot',
    ),
    sc1_ymot = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample Changer 1 Axis motor',
        fmtstr = '%.2f',
        abslimits = (-0, 600),
        visibility = (),
        curvalue = 594.5,
        unit = 'mm',
    ),
    sc1 = device('nicos.devices.generic.MultiSwitcher',
        description = 'Sample Changer 1 Huber device',
        moveables = ['sc1_y', 'st1_z'],
        mapping = {
            1: [594.5, -31],
            2: [535.5, -31],
            3: [476.5, -31],
            4: [417.5, -31],
            5: [358.5, -31],
            6: [299.5, -31],
            7: [240.5, -31],
            8: [181.5, -31],
            9: [122.5, -31],
            10: [63.5, -31],
            11: [4.5, -31],
            12: [594.5, 28],
            13: [535.5, 28],
            14: [476.5, 28],
            15: [417.5, 28],
            16: [358.5, 28],
            17: [299.5, 28],
            18: [240.5, 28],
            19: [181.5, 28],
            20: [122.5, 28],
            21: [63.5, 28],
            22: [4.5, 28],
        },
        fallback = 0,
        fmtstr = '%d',
        precision = [0.05, 0.05],
        blockingmove = False,
    ),
)

alias_config = {
    'SampleChanger': {'sc1': 100},
}
