description = 'setup for the status monitor'

group = 'special'

expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(key='exp/proposal', name='Proposal'),
            Field(key='exp/title', name='Title', istext=True, width=70),
            Field(key='sample/samplename', name='Sample', istext=True, width=30),
        ),
        BlockRow(
            Field(key='exp/action', name='Current status', width=100,
                  istext=True, default='Idle' ),
            Field(key='exp/lastscan', name='Last file'),
        ),
        ],
    )
)

filters = Block('Primary Beam/Filters', [
    BlockRow(
        Field(dev='saph', name='Saphir', istext=True),
        Field(dev='reactorpower', name='Power'),
        Field(dev='water', name='Water', istext=True),
        Field(dev='ms1', name='ms1'),
    ),
    BlockRow(
        Field(dev='befilter', name='Be', istext=True),
        Field(dev='tbefilter', name='BeT'),
        Field(dev='beofilter', name='BeO', istext=True),
        Field(dev='pgfilter', name='PG', istext=True),
    ),
    ],
)

primary = Block('Monochromator', [
    BlockRow(
        Field(dev='mono', name='Mono'),
        Field(key='mono/focmode', name='Focus', istext=True),
        Field(dev='mth', name='mth (A1)'),
        Field(dev='mtt', name='mtt (A2)'),
    ),
    ],
)

sample = Block('Sample stage', [
    BlockRow(
        Field(dev='stx', format='%.1f'),
        Field(dev='sty'),
        Field(dev='stz', format='%.2f'),
        Field(dev='sat'),
    ),
    BlockRow(
        Field(dev='sgx', format='%.2f'),
        Field(dev='sgy', format='%.2f'),
        Field(dev='sth', name='sth (A3)'),
        Field(dev='stt', name='stt (A4)'),
    ),
    ],
)

analyzer = Block('Analyzer', [
    BlockRow(
        Field(dev='ana', name='Ana'),
        Field(key='ana/focmode', name='Focus', istext=True),
        Field(dev='ath', name='ath (A5)', unit=''),
        Field(dev='att', name='att (A6)', unit=''),
    ),
    ],
)

collimation = Block('Collimation and Lengths', [
    BlockRow(
        Field(dev='ca1', default='None', width=5),
        Field(dev='ca2', default='None', width=5),
        Field(dev='ca3', default='None', width=5),
        Field(dev='ca4', default='None', width=5),
    ),
    BlockRow(
        Field(dev='lsm', width=5),
        Field(dev='lms', width=5),
        Field(dev='lsa', width=5),
        Field(dev='lad', width=5),
    ),
    BlockRow(
        Field(dev='ss1', width=25, istext=True),
    ),
    BlockRow(
        Field(dev='ss2', width=25, istext=True),
    ),
    ],
)



detector = Block('Detector', [
    BlockRow(
        Field(dev='timer'),
        Field(dev='mon1', format='%d'),
        Field(dev='mon2', format='%d'),
    ),
    BlockRow(
        Field(dev='det1', format='%d'),
        Field(dev='det2', format='%d'),
    ),
    ],
    setups='panda',
)

bambus = Block('Detector', [
    BlockRow(
        Field(name='time', dev='timer'),
        Field(name='mon1', dev='mon1'),
        Field(name='mon2', dev='mon2'),
    ),
    BlockRow(
        Field(name='3.0meV', key='det/value[8]', format='%d'),
        Field(name='3.5meV', key='det/value[7]', format='%d'),
        Field(name='4.0meV', key='det/value[6]', format='%d'),
    ),
    BlockRow(
        Field(name='4.5meV', key='det/value[5]', format='%d'),
        Field(name='5.0meV', key='det/value[4]', format='%d'),
    ),
    ],
    setups='bambus',
)

detector_small = Block('Detector', [
    BlockRow(
        Field(dev='timer'),
        Field(dev='mon1', format='%d'),
        Field(dev='mon2', format='%d'),
        Field(dev='det1', format='%d'),
        Field(dev='det2', format='%d'),
    ),
    ],
)

cam = Block('Camera', [
    BlockRow(
        Field(dev='camtimer'),
        Field(dev='cam_temp'),
    ),
    BlockRow(
        Field(key='exp/lastpoint', name='Last pict'),
    ),
    ],
    setups='camera',
)

# for setup lakeshore
lakeshore = Block('LakeShore', [
    BlockRow(
        Field(dev='t_ls340', name='Regul.'),
        Field(dev='t_ls340_a', name='Sensor A'),
        Field(dev='t_ls340_b', name='Sensor B'),
    ),
    BlockRow(
        Field(key='t_ls340/setpoint', name='Setpoint'),
        Field(key='t_ls340/p', name='P', width=5),
        Field(key='t_ls340/i', name='I', width=5),
        Field(key='t_ls340/d', name='D', width=5),
    ),
    ],
    setups='lakeshore',
)

lakeshore_hts = Block('LakeShore HTS', [
    BlockRow(
        Field(dev='t_ls_hts', name='Regul.'),
        Field(dev='t_ls_hts_a', name='Sensor A'),
        Field(dev='t_ls_hts_d', name='Sensor D'),
    ),
    BlockRow(
        Field(key='t_ls_hts/setpoint', name='Setpoint'),
        Field(key='t_ls_hts/p', name='P', width=5),
        Field(key='t_ls_hts/i', name='I', width=5),
        Field(key='t_ls_hts/d', name='D', width=5),
    ),
    ],
    setups='lakeshore_hts',
)

lakeshoreplot = Block('LakeShore', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=25, height=25, plotwindow=300,
              devices=['t_ls340/setpoint', 't_ls340_a', 't_ls340_b'],
              names=['Setpoint', 'A', 'B'],
        ),
    ),
    ],
    setups='lakeshore',
)


# generic Cryo-stuff
cryos = []
cryosupps = []
cryoplots = []
for cryo in configdata('config_frm2.all_ccis'):
    cryos.append(SetupBlock(cryo))
    cryosupps.append(SetupBlock(cryo, 'pressures'))
    cryoplots.append(SetupBlock(cryo, 'plots'))


# generic CCR-stuff
ccrs = [SetupBlock(ccr) for ccr in configdata('config_frm2.all_ccrs')]
ccrplots = [SetupBlock(ccr, 'plots')
            for ccr in configdata('config_frm2.all_ccrs')]

miramagnet = SetupBlock('miramagnet')

# for setup magnet frm2-setup
ccm5v5 = SetupBlock('ccm5v5')
ccm5v5supp = SetupBlock('ccm5v5', 'temperatures')

# for setup magnet jcns
wm5v = Block('5T Magnet', [
    BlockRow(
        Field(dev='I_wm5v'),
        Field(key='I_wm5v/target', name='Target', fmtstr='%.2f'),
    ),
    ],
    setups='wm5v',
)

wm5vsupp = Block('Magnet', [
    BlockRow(
        Field(dev='T_wm5v_sample', name='Ts'),
        Field(dev='T_wm5v_vti', name='T'),
        Field(key='T_wm5v_sample/setpoint', name='Setpoint', min=1, max=200),
    ),
    BlockRow(
        Field(dev='wm5v_lhe', name='He level'),
        Field(dev='T_wm5v_magnet', name='T (coils)'),
        Field(dev='wm5v_nv_manual', name='NV'),
    ),
    BlockRow(
        Field(dev='wm5v_piso', name='p(iso)'),
        Field(dev='wm5v_psample', name='p(sa.)', fontsize = 12),
        Field(dev='wm5v_pvti', name='p(vti)'),
    ),
    ],
    setups='wm5v',
)

wm5vplots = Block('JVM 5', [
    BlockRow(
        Field(dev='wm5v_pvti', plot='p',
            plotwindow=3600, width=30, height=20),
        Field(dev='wm5v_nv_manual', plot='p',
            plotwindow=3600, width=30, height=20),
        ),
    BlockRow(
        Field(dev='T_wm5v_vti', plot='Tmag',
            plotwindow=12*3600, width=30, height=20),
        Field(dev='T_wm5v_sample', plot='Tmag',
            plotwindow=12*3600, width=30, height=20),
        ),
    BlockRow(
        Field(dev='wm5v_lhe', plot='lhe',
            plotwindow=12*3600, width=30, height=20),
        ),
    ],
    setups='wm5v',
)

ccm12v = Block('12T Magnet', [
    BlockRow(
        Field(dev='B_ccm12v'),
        Field(key='B_ccm12v/target', name='Target', fmtstr='%.2f'),
    ),
    BlockRow(
        Field(dev='T_ccm12v_vti', name='VTI'),
        Field(dev='T_ccm12v_stick', name='Stick'),
    ),
    ],
    setups='ccm12v',
)

ccm12vplots = Block('12T Magnet', [
    BlockRow(
        Field(dev='T_ccm12v_vti', plot='Tccm12v',
            plotwindow=12*3600, width=30, height=20),
        Field(dev='T_ccm12v_stick', plot='Tccm12v',
            plotwindow=12*3600, width=30, height=20),
        ),
    ],
    setups='ccm12v',
)

foki = Block('Foki', [
    BlockRow(
        Field(dev='mfh'),
        Field(dev='mfv'),
    ),
    BlockRow(Field(dev='afh')),
    ],
)

memograph = Block('Water Flow', [
    BlockRow(
        Field(dev='cooling_flow_in', name='In'),
        Field(dev='cooling_flow_out', name='Out'),
    ),
    BlockRow(
        Field(dev='cooling_t_in', name='T In'),
        Field(dev='cooling_t_out', name='T Out'),
    ),
    BlockRow(Field(dev='cooling_leak', name='leak')),
    ],
)

column1 = Column(filters, primary, sample, analyzer) + Column(ccm5v5)
column2 = Column(collimation, detector, bambus, lakeshore_hts, ccm12v) + Column(*cryos) + Column(*ccrs) + \
          Column(lakeshore, miramagnet, wm5v)

column3 = Column(ccm5v5supp, wm5vsupp, foki, memograph, cam) + \
          Column(*cryosupps)

column4 = Column(*cryoplots) + Column(*ccrplots) + \
          Column(wm5vplots) + Column(ccm12vplots) + \
          Column(lakeshoreplot)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'PANDA status monitor',
        loglevel = 'info',
        cache = 'phys.panda.frm2',
        prefix = 'nicos/',
        font = 'Liberation Sans',
        fontsize = 16,
        valuefont = 'Fira Code',
        layout = [Row(expcolumn),
                  Row(column1, column2, column3, column4)],
    )
)
