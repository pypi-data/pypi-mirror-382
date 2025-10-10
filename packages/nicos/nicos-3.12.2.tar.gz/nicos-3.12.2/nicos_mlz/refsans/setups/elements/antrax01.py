description = 'Antrax plug switching box'

group = 'plugplay'

instrument_values = configdata('instrument.values')
lowlevel = ()

tango_url = instrument_values['tango_url'] % setupname

devices = {
    f'{setupname}': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Plug switching device',
        tangodevice = tango_url + 'box/switchbox/switch',
        unit = '',
        mapping = {
            'off': 0,
            'on': 1,
        },
        visibility = lowlevel,
    ),
}
