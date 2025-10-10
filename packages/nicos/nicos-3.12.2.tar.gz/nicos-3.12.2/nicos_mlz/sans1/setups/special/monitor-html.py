description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Current status', key='exp/action', width=90,
                  istext=True, maxlen=90),
            Field(name='Last file', key='exp/lastpoint'),
            Field(name='Current Sample', key='sample/samplename', width=26),
        ),
        ],
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
            Field(name='selector_rpm', dev='selector_rpm', width=16),
            Field(name='selector_lambda', dev='selector_lambda', width=16),
        ),
        BlockRow(
            Field(name='selector_ng', dev='selector_ng', width=16),
            Field(name='selector_tilt', dev='selector_tilt', width=16),
        ),
        BlockRow(
            Field(name='water flow', dev='selector_wflow', width=16),
            Field(name='rotor temp.', dev='selector_rtemp', width=16),
        ),
        ],
    ),
)

_instrumentshutter= Column(
    Block('Shutter', [
        BlockRow(
                 Field(name='Position', dev='instrument_shutter', width=11),
                ),
        ],
    ),
)

_ubahncolumn = Column(
    Block('U-Bahn', [
        BlockRow(
            Field(name='Train', dev='Ubahn'),
        ),
        ],
    ),
)

_meteocolumn = Column(
    Block('Outside Temp', [
        BlockRow(
            Field(name='Temp', dev='OutsideTemp', width=12),
        ),
        ],
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
            # Field(name='Col Pump', dev='coll_pump'),
            Field(name='Col Tube', dev='coll_tube'),
            Field(name='Col Nose', dev='coll_nose'),
            Field(name='Det Nose', dev='det_nose'),
            Field(name='Det Tube', dev='det_tube'),
        ),
        ],
    ),
)

_table = Column(
    Block('Sample Table', [
        BlockRow(
            Field(name='st_phi', dev='st_phi', width=13),
            Field(name='st_y', dev='st_y', width=13),
        ),
        BlockRow(
            Field(name='st_chi', dev='st_chi', width=13),
            Field(name='st_z', dev='st_z', width=13),
        ),
        BlockRow(
            Field(name='st_omg', dev='st_omg', width=13),
            Field(name='st_x', dev='st_x', width=13),
        ),
        ],
        setups='sample_table',
    ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
            Field(name='Reactor', dev='ReactorPower', width=12),
            Field(name='6 Fold Shutter', dev='Sixfold', width=12),
            Field(name='NL4a', dev='NL4a', width=12),
        ),
        BlockRow(
            Field(name='T in', dev='t_in_memograph', width=12, unit='C'),
            Field(name='T out', dev='t_out_memograph', width=12, unit='C'),
            Field(name='Cooling', dev='cooling_memograph', width=12,
                  unit='kW'),
        ),
        BlockRow(
             Field(name='Flow in', dev='flow_in_memograph', width=12,
                   unit='l/min'),
             Field(name='Flow out', dev='flow_out_memograph', width=12,
                   unit='l/min'),
             Field(name='Leakage', dev='leak_memograph', width=12,
                   unit='l/min'),
        ),
        BlockRow(
             Field(name='P in', dev='p_in_memograph', width=12, unit='bar'),
             Field(name='P out', dev='p_out_memograph', width=12,
                   unit='bar'),
             Field(name='Crane Pos', dev='Crane', width=12),
        ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
            Field(name='t', dev='det1_timer', width=13),
            Field(name='t preset', key='det1_timer/preselection', width=13),
        ),
        BlockRow(
            Field(name='det1_hv', dev='det1_hv_ax', width=13),
            Field(name='det1_z', dev='det1_z', width=13),
        ),
        BlockRow(
            Field(name='det1_omg', dev='det1_omg', width=13),
            Field(name='det1_x', dev='det1_x', width=13),
        ),
        BlockRow(
            Field(name='bs1', dev='bs1', width=13),
            Field(name='bs1_shape', dev='bs1_shape', width=13),
        ),
        BlockRow(
            Field(name='events', dev='det1_ev', width=13),
        ),
        BlockRow(
            Field(name='mon 1', dev='det1_mon1', width=13),
            Field(name='mon 2', dev='det1_mon2', width=13),
        ),
        ],
    ),
)

_atpolcolumn = Column(
    Block('Attenuator / Polarizer',[
        BlockRow(
            Field(dev='att', name='att', width=12),
        ),
        BlockRow(
            Field(dev='ng_pol', name='ng_pol', width=12),
        ),
        ],
    ),
)

_sanscolumn = Column(
    SetupBlock('collimation', 'html'),
)

_miramagnet = Column(SetupBlock('miramagnet'))
_miramagnet_plot = Column(SetupBlock('miramagnet', 'plot'))

_amagnet = Column(SetupBlock('amagnet'))
_amagnet_plot = Column(SetupBlock('amagnet', 'plot'))

_sc1 = Column(
    Block('Sample Changer 1', [
         BlockRow(
            Field(name='Position', dev='sc_y'),
            Field(name='SampleChanger', dev='sc1'),
        ),
        ],
        setups='sc1',
    ),
)

_sc2 = Column(
    Block('Sample Changer 2', [
         BlockRow(
            Field(name='Position', dev='sc_y'),
            Field(name='SampleChanger', dev='sc2'),
        ),
        ],
        setups='sc2',
    ),
)

_sc_t = Column(
    Block('Temperature Sample Changer', [
         BlockRow(
            Field(name='Position', dev='sc_y'),
            Field(name='SampleChanger', dev='sc_t'),
        ),
        ],
        setups='sc_t',
    ),
)

_ccmsanssc = Column(
    Block('Magnet Sample Changer', [
         BlockRow(
            Field(name='Position', dev='ccmsanssc_axis'),
        ),
         BlockRow(
            Field(name='SampleChanger', dev='ccmsanssc_position', format='%i'),
        ),
         BlockRow(
            Field(name='Switch', dev='ccmsanssc_switch'),
        ),
        ],
        setups='ccmsanssc',
    ),
)

_htf03 = Column(
    Block('HTF03', [
        BlockRow(
            Field(name='Temperature', dev='T_htf03', format='%.2f'),
            Field(name='Target', key='t_htf03/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_htf03/setpoint', format='%.1f'),
            Field(name='Heater Power', key='t_htf03/heaterpower', format='%.1f'),
        ),
        ],
        setups='htf03',
    ),
)

_htf03_plot = Column(
    Block('HTF03 plot', [
        BlockRow(
            Field(plot='30 min htf03', name='30 min', dev='T_htf03',
                  width=60, height=40, plotwindow=1800),
            Field(plot='30 min htf03', name='Setpoint',
                  key='T_htf03/setpoint'),
             Field(plot='30 min htf03', name='Target', key='T_htf03/target'),
             Field(plot='12 h htf03', name='12 h', dev='T_htf03', width=60,
                   height=40, plotwindow=12*3600),
             Field(plot='12 h htf03', name='Setpoint',
                   key='T_htf03/setpoint'),
             Field(plot='12 h htf03', name='Target', key='T_htf03/target'),
        ),
        ],
        setups='htf03',
    ),
)

_irf01 = Column(
    Block('IRF01', [
        BlockRow(
            Field(name='Temperature', dev='T_irf01', format='%.2f'),
            Field(name='Target', key='t_irf01/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_irf01/setpoint', format='%.1f'),
            Field(name='Heater Power', key='t_irf01/heaterpower', format='%.1f'),
        ),
        ],
        setups='irf01',
    ),
)

_irf01_plot = Column(
    Block('IRF01 plot', [
        BlockRow(
             Field(plot='30 min irf01', name='30 min', dev='T_irf01',
                   width=60, height=40, plotwindow=1800),
             Field(plot='30 min irf01', name='Setpoint',
                   key='T_irf01/setpoint'),
             Field(plot='30 min irf01', name='Target', key='T_irf01/target'),
             Field(plot='12 h irf01', name='12 h', dev='T_irf01', width=60,
                   height=40, plotwindow=12*3600),
             Field(plot='12 h irf01', name='Setpoint',
                   key='T_irf01/setpoint'),
             Field(plot='12 h irf01', name='Target', key='T_irf01/target'),
        ),
        ],
        setups='irf01',
    ),
)

_irf10 = Column(
    Block('IRF10', [
        BlockRow(
            Field(name='Temperature', dev='T_irf10', format='%.2f'),
            Field(name='Target', key='t_irf10/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_irf10/setpoint', format='%.1f'),
            Field(name='Heater Output', key='t_irf10/heateroutput', format='%.1f'),
        ),
        ],
        setups='irf10',
    ),
)

_irf10_plot = Column(
    Block('IRF10 plot', [
        BlockRow(
             Field(plot='30 min irf10', name='30 min', dev='T_irf10',
                   width=60, height=40, plotwindow=1800),
             Field(plot='30 min irf10', name='Setpoint',
                   key='T_irf10/setpoint'),
             Field(plot='30 min irf10', name='Target', key='T_irf10/target'),
             Field(plot='12 h irf10', name='12 h', dev='T_irf10', width=60,
                   height=40, plotwindow=12*3600),
             Field(plot='12 h irf10', name='Setpoint',
                   key='T_irf10/setpoint'),
             Field(plot='12 h irf10', name='Target', key='T_irf10/target'),
        ),
        ],
        setups='irf10',
    ),
)

_htf01 = Column(
    Block('HTF01', [
        BlockRow(
            Field(name='Temperature', dev='T_htf01', format='%.2f'),
            Field(name='Target', key='t_htf01/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_htf01/setpoint', format='%.1f'),
            Field(name='Heater Power', key='t_htf01/heaterpower', format='%.1f'),
        ),
        ],
        setups='htf01',
    ),
)

_htf01_plot = Column(
    Block('HTF01 plot', [
        BlockRow(
             Field(plot='30 min htf01', name='30 min', dev='T_htf01',
                   width=60, height=40, plotwindow=1800),
             Field(plot='30 min htf01', name='Setpoint',
                   key='T_htf01/setpoint'),
             Field(plot='30 min htf01', name='Target', key='T_htf01/target'),
             Field(plot='12 h htf01', name='12 h', dev='T_htf01', width=60,
                   height=40, plotwindow=12*3600),
             Field(plot='12 h htf01', name='Setpoint',
                   key='T_htf01/setpoint'),
             Field(plot='12 h htf01', name='Target', key='T_htf01/target'),
        ),
        ],
        setups='htf01',
    ),
)

_p_filter = Column(
    Block('Pressure Water Filter FAK40', [
        BlockRow(
             Field(name='P in', dev='p_in_filter', width=12, unit='bar'),
             Field(name='P out', dev='p_out_filter', width=12, unit='bar'),
             Field(name='P diff', dev='p_diff_filter', width=12, unit='bar'),
        ),
        ],
    ),
)

_ccm5h = Column(SetupBlock('ccm5h'))
_ccm5h_temperature = Column(SetupBlock('ccm5h', 'temperatures'))
_ccm5h_plot = Column(SetupBlock('ccm5h', 'plot'))

_ccm2a2 = Column(SetupBlock('ccm2a2'))
_ccm2a2_temperature = Column(SetupBlock('ccm2a2', 'temperatures'))
_ccm2a2_plot = Column(SetupBlock('ccm2a2', 'plot'))

_ccm2a5 = Column(SetupBlock('ccm2a5'))
_ccm2a5_temperature = Column(SetupBlock('ccm2a5', 'temperatures'))
_ccm2a5_plot = Column(SetupBlock('ccm2a5', 'plot'))

_ccr19_plot = Column(
    Block('30min T and Ts plot', [
        BlockRow(
            Field(plot='30 min ccr19', name='T', dev='T', width=60,
                  height=40, plotwindow=1800),
            Field(plot='30 min ccr19', name='Ts', dev='Ts'),
            Field(plot='30 min ccr19', name='Setpoint', key='T/setpoint'),
            Field(plot='30 min ccr19', name='Target', key='T/target'),
        ),
        ],
        setups='ccr19',
    ),
)

_spinflipper = Column(
    Block('Spin Flipper', [
        BlockRow(
             Field(name='P', dev='P_spinflipper'),
        ),
        BlockRow(
             Field(name='Forward', key='P_spinflipper/forward', unitkey='W'),
             Field(name='Reverse', key='P_spinflipper/reverse', unitkey='W'),
        ),
        BlockRow(
             #Field(name='Temperature', dev='T_spinflipper'),
             Field(name='Voltage', dev='U_spinflipper'),
        ),
        BlockRow(
             Field(name='A_spinflipper_hp', dev='A_spinflipper_hp'),
             Field(name='F_spinflipper_hp', dev='F_spinflipper_hp'),
        ),
        ],
        setups='spinflip',
    ),
)

rscs = [SetupBlock(rsc) for rsc in configdata('config_frm2.all_rscs')]
_rscs = Column(*rscs)

ccrs = [SetupBlock(ccr) for ccr in configdata('config_frm2.all_ccrs')]
_ccrs = Column(*ccrs)

cryos = [SetupBlock(cryo) for cryo in configdata('config_frm2.all_ccis')]
_cryos = Column(*cryos)

_julabo = Column(
    Block('Julabo', [
        BlockRow(
            Field(name='T Intern', dev='T_julabo_intern',
                   format='%.2f', unit='C', width=14),
        Field(name='Target Intern', key='T_julabo_intern/target',
                   format='%.2f', unit='C', width=14),
            Field(name='Setpoint Intern', key='T_julabo_intern/setpoint',
                   format='%.2f', unit='C', width=14),
        ),
        BlockRow(
            Field(name='T Extern', dev='T_julabo_extern',
                   format='%.2f', unit='C', width=14),
            Field(name='Target Extern', key='T_julabo_extern/target',
                   format='%.2f', unit='C', width=14),
            Field(name='Setpoint Extern', key='T_julabo_extern/setpoint',
                   format='%.2f', unit='C', width=14),
        ),
        ],
        setups='julabo',
    ),
)

_julabo_plot = Column(
    Block('Julabo plot', [
        BlockRow(
            Field(plot='julabo 30min', name='T Julabo intern',
                  dev='T_julabo_intern', width=60, height=40,
                  plotwindow=1800),
            Field(plot='julabo 30min', name='T Julabo extern',
                  dev='T_julabo_extern'),
            Field(plot='julabo 12h', name='T Julabo intern',
                  dev='T_julabo_intern', width=60, height=40,
                  plotwindow=12*3600),
            Field(plot='julabo 12h', name='T Julabo extern',
                  dev='T_julabo_extern'),
        ),
        ],
        setups='julabo',
    ),
)

_pressure_box = Column(
    Block('Pressure', [
        BlockRow(
            Field(name='Pressure', dev='pressure_box'),
        ),
        ],
        setups='pressure_box',
    ),
)

_pressure_box_plot = Column(
    Block('Pressure plot', [
        BlockRow(
            Field(plot='pressure box 30min', name='Pressure 30min',
                  dev='pressure_box', width=60, height=40,
                  plotwindow=1800),
            Field(plot='pressure box 12h', name='Pressure 12h',
                  dev='pressure_box', width=60, height=40,
                  plotwindow=12*3600),
        ),
        ],
        setups='pressure_box',
    ),
)

_dilato = Column(
    Block('Dilatometer', [
        BlockRow(
             Field(name='Temperature', dev='Ts_dil',
                   format='%.2f', unit='C', width=14),
             Field(name='Set Temp', dev='dil_set_temp',
                   format='%.2f', unit='C', width=14),
        ),
        BlockRow(
             Field(name='Length change', dev='dil_dl',
                   format='%.2f', unit='um', width=14),
             Field(name='Force', dev='dil_force',
                   format='%.2f', unit='N', width=14),
        ),
        BlockRow(
             Field(name='Power', dev='dil_power',
                   format='%.2f', unit='%', width=14),
             Field(name='Time', dev='dil_time',
                   format='%.2f', unit='s', width=14),
        ),
        ],
        setups='dilato',
    ),
)

_dilato_plot = Column(
    Block('Dilatometer plot temperature', [
        BlockRow(
             Field(plot='30 min dil', name='30 min', dev='Ts_dil',
                   width=60, height=40, plotwindow=1800),
             Field(plot='30 min dil', name='setpoint', dev='dil_set_temp',
                   width=60, height=40, plotwindow=1800),
             Field(plot='12 h dil', name='12 h', dev='Ts_dil',
                   width=60, height=40, plotwindow=12*3600),
             Field(plot='12 h dil', name='setpoint', dev='dil_set_temp',
                   width=60, height=40, plotwindow=12*3600),
        ),
        ],
        setups='dilato',
    ),
)

_dilato_plot2 = Column(
    Block('Dilatometer plot length change', [
        BlockRow(
            Field(plot='30 min dil2', name='30 min', dev='dil_dl',
                  width=60, height=40, plotwindow=1800),
            Field(plot='12 h dil2', name='12 h', dev='dil_dl',
                  width=60, height=40, plotwindow=12*3600),
        ),
        ],
        setups='dilato',
    ),
)

_dilato_plot3 = Column(
    Block('Dilatometer plot force', [
        BlockRow(
            Field(plot='30 min dil3', name='30 min', dev='dil_force',
                  width=60, height=40, plotwindow=1800),
            Field(plot='12 h dil3', name='12 h', dev='dil_force',
                  width=60, height=40, plotwindow=12*3600),
        ),
        ],
        setups='dilato',
    ),
)

_tisane_fc = Column(
    Block('TISANE Frequency Counter', [
        BlockRow(
            Field(name='Frequency', dev='tisane_fc', format='%.2e', width=12),
        ),
        ],
        setups='tisane',
    ),
)

_tisane_counts = Column(
    Block('TISANE Counts', [
        BlockRow(
            Field(name='Counts', dev='TISANE_det_pulses', width=12),
        ),
        ],
        setups='tisane',
    ),
)

_chop_phase = Column(
    Block('Phase Positions', [
        BlockRow(
            Field(name='1', dev='chopper_ch1_phase', unit='deg', format='%.2f'),
            Field(name='2', dev='chopper_ch2_phase', unit='deg', format='%.2f'),
            Field(name='water', dev='chopper_waterflow', width=8, format = '%.2'),
        ),
        ],
        setups='chopper_phase',
    ),
)

_live = Column(
    Block('Live image of Detector', [
        BlockRow(
            Field(name='Data (lin)', picture='sans1-online/live_lin.png',
                  width=64, height=64),
            Field(name='Data (log)', picture='sans1-online/live_log.png',
                  width=64, height=64),
        ),
        ],
    ),
)

_col_slit = Column(
    Block('Slit Positions', [
        BlockRow(
            Field(name='Top', dev='slit_top', unit='mm', format='%.2f',
                  width=12),
        ),
        BlockRow(
            Field(name='Left', dev='slit_left', unit='mm', format='%.2f',
                  width=12),
            Field(name='Right', dev='slit_right', unit='mm', format='%.2f',
                  width=12),
        ),
        BlockRow(
            Field(name='Bottom', dev='slit_bottom', unit='mm',
                  format='%.2f', width=12),
        ),
        BlockRow(
            Field(name='Slit [width x height]', dev='slit', unit='mm'),
        ),
        ],
    ),
)

_helios01 = Column(SetupBlock('helios01'))

_wuts = Column(*(SetupBlock(wut) for wut in ['wut-0-10-01', 'wut-0-10-02', 'wut-4-20-01', 'wut-4-20-02']))

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'SANS-1 Status monitor',
        filename = '/control/webroot/index.html',
        interval = 10,
        loglevel = 'info',
        cache = 'ctrl.sans1.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [
            Row(_expcolumn),
            Row(_sans1general, _table, _sans1det),
            Row(_ubahncolumn, _meteocolumn, _pressurecolumn, _p_filter),
            Row(_instrumentshutter, _selcolumn, _chop_phase, _col_slit, _atpolcolumn, _sanscolumn),
            Row(_ccm5h, _ccm5h_temperature,
                _ccm2a2, _ccm2a2_temperature,
                _ccm2a5, _ccm2a5_temperature,
                _spinflipper, _ccrs, _cryos, _sc1, _sc2,
                _sc_t, _ccmsanssc, _miramagnet, _amagnet,
                _htf03, _htf01, _irf01, _irf10, _rscs, _julabo,
                _tisane_counts, _tisane_fc, _helios01, _wuts, _dilato,
                _pressure_box),
            Row(_ccm5h_plot, _ccm2a2_plot, _ccm2a5_plot, _ccr19_plot,
                _htf03_plot, _irf01_plot, _irf10_plot, _htf01_plot, _julabo_plot,
                _miramagnet_plot, _amagnet_plot, _dilato_plot, _pressure_box_plot),
            Row(_dilato_plot2),
            Row(_dilato_plot3),
            Row(_live),
        ],
        noexpired = True,
    ),
)
