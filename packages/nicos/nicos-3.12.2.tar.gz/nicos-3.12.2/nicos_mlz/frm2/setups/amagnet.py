description = 'ANTARES garfield magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = f'tango://{setupname}:10000/box/'

devices = dict(
    # monitoring devices
    amagnet_T1 = device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature1 of the coils system',
        tangodevice = tango_base + 'plc/_t1',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_T2 = device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature2 of the coils system',
        tangodevice = tango_base + 'plc/_t2',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_T3 = device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature3 of the coils system',
        tangodevice = tango_base + 'plc/_t3',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_T4 = device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature4 of the coils system',
        tangodevice = tango_base + 'plc/_t4',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_IMonitor = device('nicos.devices.entangle.AnalogInput',
        description = 'Monitors the current via the PLC',
        tangodevice = tango_base + 'plc/_i_monitor',
        visibility = (),
    ),
    amagnet_UMonitor = device('nicos.devices.entangle.AnalogInput',
        description = 'Monitors the voltage via the PLC',
        tangodevice = tango_base + 'plc/_u_monitor',
        visibility = (),
    ),
    amagnet_unipolar = device('nicos.devices.entangle.AnalogInput',
        description = 'Monitors the current ramping device in the PLC',
        tangodevice = tango_base + 'plc/_unipolar',
        visibility = (),
    ),
    # previously used to control the current, now just for monitoring
    amagnet_pscurrent = device('nicos.devices.entangle.PowerSupply',
        description = 'Device for the magnet power supply (current mode)',
        tangodevice = tango_base + 'lambda/curr',
        unit = 'A',
        abslimits = (0, 200),
        precision = 0.05,
        visibility = (),
    ),

    # control devices
    amagnet_enable = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Garfield magnet: on/off switch',
        tangodevice = tango_base + 'plc/_enable',
        mapping = dict(
            on = 1, off = 0
        ),
        unit = '',
    ),
    amagnet_polarity = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Garfield magnet: polarity (+/-) switch',
        tangodevice = tango_base + 'plc/_polarity',
        # 0 is shorting the power-supply: only if current is zero!
        # there is an interlock in the plc:
        # if there is current, switching polarity is forbidden
        # if polarity is short, powersupply is disabled
        mapping = {'+1': 1,
                   '0': 0,
                   '-1': -1},
        unit = '',
        visibility = (),  # handled by current control device
    ),
    amagnet_symmetry = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Garfield magnet: par/ser switch selecting (a)symmetric mode',
        tangodevice = tango_base + 'plc/_symmetric',
        # symmetric is serial, asymmetric is parallel
        mapping = dict(
            symmetric = 1, short = 0, unsymmetric = -1
        ),
        unit = '',
    ),
    I_amagnet = device('nicos.devices.entangle.RampActuator',
        description = 'Main current control device in the plc, handles also the polarity switching and ramping',
        tangodevice = tango_base + 'plc/_i',
        fmtstr = '%.1f',
    ),
    # by convention this needs to be B_%(setupname)s
    B_amagnet = device('nicos_mlz.devices.amagnet.GarfieldMagnet',
        description = 'magnetic field device, handling polarity switching and stuff',
        currentsource = 'I_amagnet',
        # currentreadback = 'I_amagnet',
        currentreadback = 'amagnet_pscurrent',
        enable = 'amagnet_enable',  # for auto-enable
        symmetry = 'amagnet_symmetry',  # for calibration-selection
        unit = 'T',
        # B(I) = c[0]*I + c[1]*erf(c[2]*I) + c[3]*atan(c[4]*I)
        # 2016/10/12: Kalibrierkuve.xls from T.Reimann
        calibrationtable = dict(
            symmetric = (
                0.00186517, 0.0431937, -0.185956, 0.0599757, 0.194042
            ),
            short = (0.0, 0.0, 0.0, 0.0, 0.0),
            unsymmetric = (
                0.00136154, 0.027454, -0.120951, 0.0495289, 0.110689
            ),
        ),
        userlimits = (-0.35, 0.35),
        fmtstr = '%.4f',
    ),
)

alias_config = {'B': {'B_amagnet': 100},
                'I': {'I_amagnet' : 80},  # for the rare case of direct current control needed
}

extended = dict(
    representative = 'B_amagnet',
)

monitor_blocks = dict(
    default = Block('Antares Magnet', [
        BlockRow(
            Field(name='Field', dev='B_amagnet', width=12),
            Field(name='Target', key='B_amagnet/target', width=12),
        ),
        BlockRow(
            Field(name='Current', dev='I_amagnet', width=12),
            Field(name='ON/OFF', dev='amagnet_enable', width=12),
        ),
        BlockRow(
            Field(name='Polarity', dev='amagnet_polarity', width=12),
            Field(name='Symmetry', dev='amagnet_symmetry', width=12),
        ),
        BlockRow(
            Field(name='Lambda out', dev='amagnet_pscurrent', width=12),
        ),
    ], setups=setupname),
    plot = Block('Antares Magnet plot', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=60, height=15, plotwindow=1800,
                  devices=['B_amagnet', 'b_amagnet/target'],
                  names=['30min', 'Target'],
                  legend=True),
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=60, height=15, plotwindow=12*3600,
                  devices=['B_amagnet', 'b_amagnet/target'],
                  names=['12h', 'Target'],
                  legend=True),
        ),
    ], setups=setupname),
)
