description = 'PANDA Cu-monochromator'

group = 'lowlevel'

includes = ['monofoci', 'monoturm', 'panda_mtt']

excludes = ['mono_pg', 'mono_si', 'mono_heusler']

extended = dict(dynamic_loaded = True)

devices = dict(
    mono_cu = device('nicos.devices.tas.Monochromator',
        description = 'PANDA Cu monochromator',
        unit = 'A-1',
        theta = 'mth',
        twotheta = 'mtt',
        reltheta = True,
        focush = 'mfh_cu',
        focusv = 'mfv_cu',
        hfocuspars = [0],
        vfocuspars = [0],
        abslimits = (1, 10),
        material = 'Cu',
        reflection = (1, 1, 1),
        dvalue = 2.08,
        scatteringsense = -1,
        crystalside = -1,
        fixed = 'Please give me correct parameters first!',
        fixedby = ('brain', 99),
    ),
    mfh_cu_step = device('nicos_virt_mlz.panda.devices.stubs.MccMotor',
        description = 'horizontal focusing MOTOR of Cu monochromator',
        fmtstr = '%.3f',
        abslimits = (1, 5),
        unit = 'mm',
        speed = 5.0 / 54.0,
        visibility = (),
    ),
    mfh_cu_poti = device('nicos.devices.generic.VirtualCoder',
        description = 'horizontal focusing CODER of Cu monochromator',
        motor = 'mfh_cu_step',
        fmtstr = '%.3f',
        unit = 'mm',
        visibility = (),
    ),
    mfh_cu = device('nicos.devices.generic.Axis',
        description = 'horizontal focus of Cu monochromator',
        motor = 'mfh_cu_step',
        obs = ['mfh_cu_poti'],
        precision = 0.01,
        backlash = 0,
        visibility = (),
        fixed = 'Please give me correct parameters first!',
        fixedby = ('brain', 99),
    ),
    mfv_cu_step = device('nicos_virt_mlz.panda.devices.stubs.MccMotor',
        description = 'vertical focusing MOTOR of Cu monochromator',
        fmtstr = '%.3f',
        abslimits = (1, 5),
        unit = 'mm',
        speed = 5.0 / 54.0,
        visibility = (),
    ),
    mfv_cu_poti = device('nicos.devices.generic.VirtualCoder',
        description = 'vertical focusing CODER of Cu monochromator',
        motor = 'mfv_cu_step',
        fmtstr = '%.3f',
        unit = 'mm',
        visibility = (),
    ),
    mfv_cu = device('nicos.devices.generic.Axis',
        description = 'vertical focus of Cu monochromator',
        motor = 'mfv_cu_step',
        obs = ['mfv_cu_poti'],
        precision = 0.01,
        backlash = 0,
        visibility = (),
        fixed = 'Please give me correct parameters first!',
        fixedby = ('brain', 99),
    ),
)

startupcode = '''
try:
    _ = (ana, mono, mfv, mfh, focibox)
except NameError as e:
    printerror("The requested setup 'panda' is not fully loaded!")
    raise NameError('One of the required devices is not loaded : %s, please check!' % e)

if focibox.read(0) == 'Cu':
    from nicos import session
    mfh.alias = session.getDevice('mfh_cu')
    mfv.alias = session.getDevice('mfv_cu')
    mono.alias = session.getDevice('mono_cu')
    ana.alias = session.getDevice('ana_pg')
    mfh.motor._pushParams() # forcibly send parameters to HW
    mfv.motor._pushParams() # forcibly send parameters to HW
    focibox.comm('XMA',forcechannel=False) # enable output for mfh
    focibox.comm('YMA',forcechannel=False) # enable output for mfv
    focibox.driverenable = True
    maw(mtx, 0) #correct center of rotation for Si-mono only
    del session
else:
    printerror('WRONG MONO ON TABLE FOR SETUP mono_cu !!!')
'''
