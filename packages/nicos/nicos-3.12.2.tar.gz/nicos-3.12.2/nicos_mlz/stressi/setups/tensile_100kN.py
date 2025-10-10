description = 'Tensile machine 100kN'

group = 'optional'

excludes = ['tensile']

nameservice = 'stressictrl.stressi.frm2.tum.de'

devices = dict(
    teload = device('nicos.devices.vendor.caress.Motor',
        description = 'load value of the tensile machine',
        nameserver = '%s' % nameservice,
        config = 'TELOAD 500 TensileLoad.ControllableDevice',
        absdev = False,
        abslimits = (-100000, 100000),
        unit = 'N',
        fmtstr = '%.2f',
    ),
    tepos = device('nicos.devices.vendor.caress.Motor',
        description = 'position value of the tensile machine',
        nameserver = '%s' % nameservice,
        config = 'TEPOS 500 TensilePos.ControllableDevice',
        absdev = False,
        abslimits = (-50, 50),
        unit = 'mm',
        fmtstr = '%.3f',
    ),
    teext = device('nicos.devices.vendor.caress.Motor',
        description = 'extension value of the tensile machine',
        nameserver = '%s' % nameservice,
        config = 'TEEXT 500 TensileExt.ControllableDevice',
        absdev = False,
        abslimits = (-3000, 3000),
        unit = 'um',
        fmtstr = '%.3f',
    ),
)

display_order = 40
