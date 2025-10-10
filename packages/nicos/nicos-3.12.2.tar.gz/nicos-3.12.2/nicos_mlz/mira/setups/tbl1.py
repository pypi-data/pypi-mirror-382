description = 'Huber rotation tables'

group = 'optional'

tango_base = 'tango://miractrl.mira.frm2.tum.de:10000/mira/'

devices = dict(
    tbl1 = device('nicos.devices.entangle.Motor',
        description = 'first general-use rotator table',
        tangodevice = tango_base + 'table/rot1',
        abslimits = (-360, 360),
        precision = 0.05,
    ),
)
