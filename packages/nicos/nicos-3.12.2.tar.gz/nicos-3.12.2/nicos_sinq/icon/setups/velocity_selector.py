description = 'Devices for the velocity selector'

display_order = 15

devices = dict()

pvprefix = 'SQ:ICON:'
vsreadables = dict()
vsreadables['manual'] = pvprefix + 'b1io4:VSManualRBV'
vsreadables['ready'] = pvprefix + 'b1io4:VSReadyRBV'
vsreadables['speed_rbv'] = pvprefix + 'VS:SpeedRBV'
vsreadables['vibration'] = pvprefix + 'b1io4:VSVibrationRBV'
vsreadables['inverter_on'] = pvprefix + 'b1io4:VSInverterONRBV'

vswritables = dict()
vswritables['on'] = pvprefix + 'b1io3:VSon'
vswritables['off'] = pvprefix + 'b1io3:VSoff'

vssetpwritable = dict()
vssetpwritable['setp'] = pvprefix + 'VSSP:Speed'
#vswritables['b2'] = pvprefix + 'VSSP:B2'

# hide/unhide low level devices
hide = ()

for name, pv in vsreadables.items():
    devices['vs_' + name] = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'VS %s readout' % name,
        readpv = pv,
        visibility = hide,
    )

for name, pv in vswritables.items():
    devices['vs_' + name] = device('nicos.devices.epics.pyepics.EpicsDigitalMoveable',
        description = 'VS %s switch' % name,
        readpv = pv,
        writepv = pv,
        visibility = hide,
    )

for name, pv in vssetpwritable.items():
    devices['vs_' + name] = device('nicos.devices.epics.pyepics.EpicsAnalogMoveable',
        description = 'VS %s analog' % name,
        readpv = pv,
        writepv = pv,
        visibility = hide,
        abslimits = (0, 4095),
    )

devices['vs_state'] = device('nicos_sinq.icon.devices.velocity_selector.VSState',
    description = 'Device to control the state of the velocity selector',
    visibility = hide,
    on = 'vs_on',
    off = 'vs_off',
    hand = 'vs_manual',
    ready = 'vs_ready',
    state = 'vs_inverter_on',
)

devices['vs_speed'] = device('nicos_sinq.icon.devices.velocity_selector.VSSpeed',
    description = 'Controls the speed of the velocity selector',
    state = 'vs_state',
    setp = 'vs_setp',
    #b2 = 'vs_b2',
    rbv = 'vs_speed_rbv',
    unit = 'Hz'
)

devices['vs_lambda'] = device('nicos_sinq.icon.devices.velocity_selector.VSLambda',
    description = 'Controls the wavelength of the VS',
    speed = 'vs_speed',
    unit = 'Angstroem'
)
