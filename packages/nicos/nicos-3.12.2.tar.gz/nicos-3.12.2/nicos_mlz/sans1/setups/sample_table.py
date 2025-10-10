description = 'bottom sample table devices'

group = 'lowlevel'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/sample/table/'

devices = dict(
    # use an Actuator as referencing is broken on this hw
    st_omg = device('nicos_mlz.sans1.devices.huber.HuberAxis',
        description = 'sample table omega rotation',
        tangodevice = tango_base + 'st_omg',
        fmtstr = '%.2f',
        abslimits = (-180, 180),
    ),
    st_chi = device('nicos_mlz.sans1.devices.huber.HuberAxis',
        description = 'sample table chi tilt',
        tangodevice = tango_base + 'st_chi',
        fmtstr = '%.2f',
        abslimits = (-7.5, 7.5),
    ),
    st_phi = device('nicos_mlz.sans1.devices.huber.HuberAxis',
        description = 'sample table phi tilt',
        tangodevice = tango_base + 'st_phi',
        fmtstr = '%.2f',
        abslimits = (-7.5, 7.5),
    ),
    st_y = device('nicos_mlz.sans1.devices.huber.HuberAxis',
        description = 'sample table y shift',
        tangodevice = tango_base + 'st_y',
        fmtstr = '%.2f',
        abslimits = (-99, 99),
    ),
    st_z = device('nicos_mlz.sans1.devices.huber.HuberAxis',
        description = 'sample table z',
        tangodevice = tango_base + 'st_z',
        fmtstr = '%.2f',
        abslimits = (-50, 50),
    ),
    st_x = device('nicos_mlz.sans1.devices.huber.HuberAxis',
        description = 'sample table x',
        tangodevice = tango_base + 'st_x',
        fmtstr = '%.2f',
        abslimits = (-500.9, 110.65),
#        abslimits = (-700, 150),  # keep this line !
    ),
)
