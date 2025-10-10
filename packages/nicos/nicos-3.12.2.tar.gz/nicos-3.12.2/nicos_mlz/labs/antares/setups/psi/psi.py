description = 'Tensile rig together with magnet'

includes = ['doli', 'lambdas', 'pibox01']

devices = dict(
    currentsw = device('nicos.devices.generic.LockedDevice',
        description = 'Polarity switcher',
        device = 'out_1',
        lock = 'I_lambda1',
        unlockvalue = 0,
        fmtstr = '0x%02x',
    ),
)

# startupcode = '''
# air.alias = 'out_0'
# '''

