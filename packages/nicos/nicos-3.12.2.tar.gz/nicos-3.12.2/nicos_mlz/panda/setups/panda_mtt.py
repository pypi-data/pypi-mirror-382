description = 'setup for Beckhoff PLC mtt devices on PANDA'
group = 'lowlevel'
display_order = 23

tango_base = 'tango://phys.panda.frm2:10000/panda/'
plc = tango_base + 'beckhoff_mtt/plc_'

devices = dict(
    diagnostics = device('nicos.devices.entangle.DigitalInput',
        description = 'Status of all position switches.',
        tangodevice = plc + 'diagnostics',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    diag_automove = device('nicos.devices.entangle.DigitalInput',
        description = 'Diagnostic information for function block '
        '"MTT_Auto_Move".',
        tangodevice = plc + 'diag_automove',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    diag_bccw = device('nicos.devices.entangle.DigitalInput',
        description = 'Diagnostic information for function block '
        '"MB_WECHSEL_TO_CCW".',
        tangodevice = plc + 'diag_bccw',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    diag_bcw = device('nicos.devices.entangle.DigitalInput',
        description = 'Diagnostic information for function block '
        '"MB_WECHSEL_TO_CW".',
        tangodevice = plc + 'diag_bcw',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    diag_switches = device('nicos.devices.entangle.DigitalInput',
        description = 'Status of all limit and reference switches.',
        tangodevice = plc + 'diag_switches',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    klinke_ccw = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Device for the movement of the pressed air actuator '
        'opening "Klinke CCW".',
        tangodevice = plc + 'klinke_ccw',
        visibility = (),
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    klinke_cw = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Device for the movement of the pressed air actuator '
        'opening "Klinke CW".',
        tangodevice = plc + 'klinke_cw',
        visibility = (),
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    max_ref_angle = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Maximum absolute value of the angle that is used for '
        'the block gap search algorithm during MTT referencing in CW direction.',
        tangodevice = plc + 'max_ref_angle',
        visibility = (),
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    mb_arm_magnet = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Device for switching the magnet in the mobile arm on '
        'and off.',
        tangodevice = plc + 'mb_arm_magnet',
        visibility = (),
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    mb_arm_raw = device('nicos.devices.entangle.Motor',
        description = 'Mobile arm axis "MB_ARM".',
        tangodevice = plc + 'mb_arm_raw',
        visibility = (),
    ),
    mb_arm_inc_encoder = device('nicos.devices.entangle.Sensor',
        description = 'Normalized value of the "MB_ARM" axis incremental '
        'encoder.',
        tangodevice = plc + 'mbarmincencoder',
        visibility = (),
        unit = 'steps',
    ),
    mb_arm_error = device('nicos.devices.entangle.DigitalInput',
        description = 'Beckhoff error code for axis "MB_ARM".',
        tangodevice = plc + 'diag_arm_err',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    mtt = device('nicos_mlz.panda.devices.debug.InvertablePollMotor',
        description = 'Virtual MTT axis that exchanges block automatically '
                      '(must be used in "automatic" mode).',
        tangodevice = plc + 'mtt',
        unit = 'deg',
        invert = False,
        polldevs = [
            "diagnostics", "diag_switches",
            "mb_arm_magnet", "mb_arm_raw",
        ],
    ),
    mtt_abs_encoder = device('nicos.devices.entangle.Sensor',
        description = 'Normalized value of the "MTT_RAW" axis absolute '
        'encoder.',
        tangodevice = plc + 'mttabsencoder',
        unit = 'steps',
    ),
    mtt_inc_encoder = device('nicos.devices.entangle.Sensor',
        description = 'Normalized value of the "MTT_RAW" axis incremental '
        'encoder.',
        tangodevice = plc + 'mttincencoder',
        visibility = (),
        unit = 'steps',
    ),
    mtt_err = device('nicos.devices.entangle.DigitalInput',
        description = 'Beckhoff error code for axis "MTT_RAW".',
        tangodevice = plc + 'diag_mtt_err',
        visibility = (),
        fmtstr = '%#x',
        unit = '',
    ),
    mtt_raw = device('nicos.devices.entangle.Motor',
        description = 'Raw MTT axis without automatic block exchange (must be '
        ' used in manual mode).',
        tangodevice = plc + 'mtt_raw',
        visibility = (),
        unit = 'deg',
    ),
    n_blocks_cw = device('nicos.devices.entangle.DigitalOutput',
        description = 'Number of blocks on the CW side of the block gap '
        '(channel for the incoming beam).',
        tangodevice = plc + 'n_blocks_cw',
        visibility = (),
        fmtstr = '%d',
        unit = 'blocks',
    ),
    opmode = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Current MTT operational mode.',
        tangodevice = plc + 'opmode',
        requires = {'level': 'admin'},
        visibility = (),
        fmtstr = '%d',
        unit = '',
        mapping = {
            'automatic mode': 0,
            'manual mode': 1,
            'radiant leak allowed': 2,
        },
    ),
)

startupcode = '''
CreateDevice('diagnostics')
CreateDevice('diag_automove')
CreateDevice('diag_bccw')
CreateDevice('diag_bcw')
CreateDevice('diag_switches')
CreateDevice('klinke_ccw')
CreateDevice('klinke_cw')
CreateDevice('max_ref_angle')
CreateDevice('mb_arm_magnet')
CreateDevice('mb_arm_raw')
CreateDevice('mb_arm_error')
CreateDevice('mb_arm_inc_encoder')
CreateDevice('mtt_inc_encoder')
CreateDevice('mtt_err')
CreateDevice('mtt_raw')
CreateDevice('n_blocks_cw')
CreateDevice('opmode')
'''
