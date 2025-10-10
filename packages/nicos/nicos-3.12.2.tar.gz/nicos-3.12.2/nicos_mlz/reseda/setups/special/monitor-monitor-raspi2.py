description = 'setup for the right status monitor'
group = 'special'

_guidefields = Column(
    Block('Guide Fields', [
        BlockRow(
            Field(dev='gf0'),
            Field(dev='gf1'),
            Field(dev='gf2'),
            Field(dev='gf4'),
            Field(dev='gf5'),
            Field(dev='gf6'),
            Field(dev='gf7'),
            Field(dev='gf8'),
            Field(dev='gf9'),
            Field(dev='gf10'),
        ),
        ],
        setups = 'guide_fields',
    ),
)

_column1 = Column(
    Block('arm0a', [
        BlockRow(
            Field(name='SF0a', dev='sf_0a'),
            Field(name='HSF0a', dev='hsf_0a'),
        ),
        BlockRow(
            Field(name='RF0a', dev='cbox_0a_reg_amp'),
            Field(name='HRF0a', dev='hrf_0a'),
        ),
        BlockRow(
            Field(name='Freq', dev='cbox_0a_fg_freq'),
        ),
        # BlockRow(
        #     Field(name='FP', dev='cbox_0a_fwdp'),
        #     Field(name='RP', dev='cbox_0a_rwp'),
        # ),
        BlockRow(
            Field(name='C1', dev='cbox_0a_coil1_c1'),
            Field(name='C2', dev='cbox_0a_coil1_c2'),
            Field(name='C3', dev='cbox_0a_coil1_c3'),
        ),
        BlockRow(
            Field(name='C1C2', dev='cbox_0a_coil1_c1c2serial'),
            Field(name='Trafo', dev='cbox_0a_coil1_transformer'),
        ),
        BlockRow(
            Field(name='Diplexer', dev='cbox_0a_diplexer'),
            Field(name='Highpass', dev='cbox_0a_highpass'),
        ),
        BlockRow(
            Field(name='Power Divider', dev='cbox_0a_power_divider'),
        ),
        ],
        setups='static_flippers and resonance_flippers and cbox_0a and arm_1',
    ),
)

_column2 = Column(
    Block('arm0b', [
        BlockRow(
            Field(name='SF0b', dev='sf_0b'),
            Field(name='HSF0b', dev='hsf_0b'),
        ),
        BlockRow(
            Field(name='RF0b', dev='cbox_0b_reg_amp'),
            Field(name='HRF0b', dev='hrf_0b'),
        ),
        BlockRow(
            Field(name='Freq', dev='cbox_0b_fg_freq'),
        ),
        BlockRow(
            Field(name='C1', dev='cbox_0b_coil1_c1'),
            Field(name='C2', dev='cbox_0b_coil1_c2'),
            Field(name='C3', dev='cbox_0b_coil1_c3'),
        ),
        BlockRow(
            Field(name='C1C2', dev='cbox_0b_coil1_c1c2serial'),
            Field(name='Trafo', dev='cbox_0b_coil1_transformer'),
        ),
        BlockRow(
            Field(name='Diplexer', dev='cbox_0b_diplexer'),
            Field(name='Highpass', dev='cbox_0b_highpass'),
        ),
        BlockRow(
            Field(name='Power Divider', dev='cbox_0b_power_divider'),
        ),
        ],
        setups='static_flippers and resonance_flippers and cbox_0b and arm_1',
    ),
)

_column3 = Column(
    Block('arm1', [
        BlockRow(
            Field(name='SF1', dev='sf_1'),
            Field(name='HSF1', dev='hsf_1'),
        ),
        BlockRow(
            Field(name='RF1', dev='cbox_1a_reg_amp'),
            Field(name='HRF1a', dev='hrf_1a'),
            Field(name='HRF1b', dev='hrf_1b'),
        ),
        BlockRow(
            Field(name='Freq', dev='cbox_1a_fg_freq'),
        ),
        BlockRow(
            Field(name='C1', dev='cbox_1a_coil1_c1'),
            Field(name='C2', dev='cbox_1a_coil1_c2'),
            Field(name='C3', dev='cbox_1a_coil1_c3'),
        ),
        BlockRow(
            Field(name='C1C2', dev='cbox_1a_coil1_c1c2serial'),
            Field(name='Trafo', dev='cbox_1a_coil1_transformer'),
        ),
        BlockRow(
            Field(name='Diplexer', dev='cbox_1a_diplexer'),
            Field(name='Highpass', dev='cbox_1a_highpass'),
        ),
        BlockRow(
            Field(name='Power Divider', dev='cbox_1a_power_divider'),
        ),
        BlockRow(
            Field(name='T Coil 1', dev='T_arm1_coil1'),
            Field(name='T Coil 2', dev='T_arm1_coil2'),
        ),
        BlockRow(
            Field(name='T Coil 3', dev='T_arm1_coil3'),
            Field(name='T Coil 4', dev='T_arm1_coil4'),
        ),
        ],
        setups='static_flippers and resonance_flippers and cbox_1a and arm_1',
    ),
)

_subcoils = Column(
    Block('Field substraction coils', [
        BlockRow(
            Field(name='NSE 0', dev='nse0'),
            Field(name='NSE 1', dev='nse1'),
            Field(name='Phase', dev='phase'),
        ),
        ],
        setups='sub_coils',
     ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'RESEDA Technical',
        loglevel = 'info',
        cache = 'resedactrl.reseda.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Consolas',
        fontsize = '13',
        padding = 4,
        colors = 'dark',
        layout = [[_guidefields], [_column1, _column2, _column3], [_subcoils]]
    ),
)
