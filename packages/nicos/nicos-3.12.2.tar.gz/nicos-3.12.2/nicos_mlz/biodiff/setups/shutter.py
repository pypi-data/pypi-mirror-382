description = 'Shutter setup'
group = 'lowlevel'

tango_base = 'tango://phys.biodiff.frm2:10000/biodiff/'

_MAP_SHUTTER = {
    'open': 1,
    'closed': 0,
}

devices = dict(
    gammashutter = device('nicos_mlz.jcns.devices.shutter.Shutter',
        description = 'Gamma shutter',
        tangodevice = tango_base + 'plcdigital/gammashutter',
        mapping = _MAP_SHUTTER,
    ),
    photoshutter = device('nicos_mlz.jcns.devices.shutter.Shutter',
        description = 'Photo shutter',
        tangodevice = tango_base + 'plcdigital/photoshutter',
        mapping = _MAP_SHUTTER,
    ),
)
