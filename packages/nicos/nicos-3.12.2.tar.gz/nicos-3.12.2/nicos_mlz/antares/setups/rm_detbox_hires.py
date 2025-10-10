description = 'High Resolution Detector Box'

group = 'optional'

excludes = ['scintillatortx']

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    scintillatortx = device('nicos.devices.entangle.Motor',
        description = 'Translation of scintillator box in X direction',
        tangodevice = tango_base + 'fzjs7/FOV',
        abslimits = (-150, 250),
        userlimits = (-150, 250),
        precision = 0.01,
    ),
)
