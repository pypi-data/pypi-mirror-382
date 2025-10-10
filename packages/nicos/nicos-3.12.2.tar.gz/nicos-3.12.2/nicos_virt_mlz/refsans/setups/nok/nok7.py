description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok7 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 1190.0 mm
        description = 'NOK7',
        fmtstr = '%.2f, %.2f',
        nok_start = 7665.5,
        nok_end = 8855.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok7r_axis',
        motor_s = 'nok7s_axis',
        nok_motor = [7915.0, 8605.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['ng'],
            'vc': global_values['vc'],
            'fc': global_values['fc'],
        },
        mode = 'ng',
    ),
    nok7r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK7, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-89.475, 116.1),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        visibility = (),
    ),
    nok7s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK7, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-96.94, 125.56),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        visibility = (),
    ),
)
