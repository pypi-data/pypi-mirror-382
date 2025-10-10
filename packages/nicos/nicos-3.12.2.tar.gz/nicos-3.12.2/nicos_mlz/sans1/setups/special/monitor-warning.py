description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20,
                  istext=True, maxlen=20),
            Field(name='Current status', key='exp/action', width=65,#70
                  istext=True, maxlen=90),
            Field(name='Data file', key='exp/lastpoint'),
            Field(name='Current Sample', key='sample/samplename', width=16),
        ),
        ],
        # setups='experiment',
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
            Field(name='selector_rpm', dev='selector_rpm', width=8),
        ),
        BlockRow(
            Field(name='selector_lambda', dev='selector_lambda', width=8),
        ),
        BlockRow(
            Field(name='selector_ng', dev='selector_ng', width=8),
        ),
        BlockRow(
            Field(name='selector_tilt', dev='selector_tilt', width=8, format = '%.1f'),
        ),
        BlockRow(
            Field(name='water flow', dev='selector_wflow', width=8, format = '%.1f'),
        ),
        BlockRow(
            Field(name='rotor temp.', dev='selector_rtemp', width=8, format = '%.1f'),
        ),
        ],
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
            # Field(name='Col Pump', dev='coll_pump', width=11, format = '%g'),
            Field(name='Col Tube', dev='coll_tube', width=11, format = '%g'),
            Field(name='Col Nose', dev='coll_nose', width=11, format = '%g'),
            Field(name='Det Nose', dev='det_nose', width=11, format = '%g'),
            Field(name='Det Tube', dev='det_tube', width=11, format = '%g'),
        ),
        ],
    ),
)

_collimationcolumn = Column(
    Block('Collimation',[
        BlockRow(
            Field(dev='att', name='att',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['dia10', 'x10','x100','x1000','open'],
                  width=6.5,height=9),
            Field(dev='ng_pol', name='ng_pol',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['col','pol2','pol1','ng'],
                  width=5.5,height=9),
            Field(dev='col_20', name='20',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['las','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_18', name='18',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='bg1', name='bg1',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['50mm','open','20mm','42mm'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
            Field(dev='col_16', name='16',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_14', name='14',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_12', name='12',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_10', name='10',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_8', name='8',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_6', name='6',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='bg2', name='bg2',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['28mm','20mm','12mm','open'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
            Field(dev='col_4', name='4',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_3', name='3',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            Field(dev='col_2', name='2',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['free2','free1','col','ng'],
                  width=5,height=9),
            # Field(dev='col_2b', name='1.5',
            #       widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
            #       options=['free2','free1','col','ng'],
            #       width=5,height=9),
            Field(dev='sa1', name='sa1',
                  widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
                  options=['20mm','30mm','50x50'],
                  disabled_options = ['N.A.'],
                  width=7,height=9),
        ),
        BlockRow(
            Field(dev='col', name='col', unit='m', format = '%.1f'),
        ),
        ],
    ),
)

_sampleaperture = Column(
    Block('SA', [
        BlockRow(
            Field(name='sa2', dev='sa2', width=6, format = '%g'),
        ),
        ],
    ),
)

_temp_garching = Column(
    Block('Temperature @ Garching', [
        BlockRow(
            Field(name='Temperature', dev='OutsideTemp'),
        ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
            Field(devices=['det1_z', 'det1_x', 'det1_omg'],
                  widget='nicos_mlz.sans1.gui.monitorwidgets.Tube2', width=30, height=10)#, max=21000),
        ),
        BlockRow(
            Field(name='det1_z', dev='det1_z', width=9, unit='mm', format='%.0f'),
            Field(name='det1_x', dev='det1_x', width=9, unit='mm', format='%.0f'),
            Field(name='det1_omg', dev='det1_omg', width=9, unit='deg', format='%.0f'),
            Field(name='t', dev='det1_timer', width=9),
            Field(name='t pres.', key='det1_timer/preselection', width=9, unit='s', format='%i'),
            Field(name='det1_hv', dev='det1_hv_ax', width=9, format='%i'),
            Field(name='events', dev='det1_ev', width=9),
            Field(name='mon 1', dev='det1_mon1', width=9),
            Field(name='mon 2', dev='det1_mon2', width=9),
            Field(name='bs1_x', dev='bs1_xax', width=9, format='%.1f'),
            Field(name='bs1_y', dev='bs1_yax', width=9, format='%.1f'),
        ),
        ],
    ),
)

_p_filter = Column(
    Block('Pressure Water Filter FAK40', [
        BlockRow(
            Field(name='P in', dev='p_in_filter', width=9.5, unit='bar'),
            Field(name='P out', dev='p_out_filter', width=9.5, unit='bar'),
            Field(name='P diff', dev='p_diff_filter', width=9.5, unit='bar'),
        ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'SANS-1 status monitor',
        loglevel = 'info',
        cache = 'ctrl.sans1.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 11,  # 12
        padding = 0,  # 3
        layout = [],
    ),
)
