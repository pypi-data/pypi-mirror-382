description = 'setup for the status monitor, HTML version'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=30,
                  istext=True),
            Field(name='Last scan file', key='exp/lastscan',
                  setups='tas'),
            Field(name='Last image file', key='exp/lastpoint',
                  setups='sans'),
        ),
        ],
    ),
)

_axisblock = Block('Axes', [
    BlockRow(
        Field(dev='mth'),
        Field(dev='mtt'),
    ),
    BlockRow(
        Field(dev='sth'),
        Field(dev='stt'),
    ),
    BlockRow(
        Field(dev='ath'),
        Field(dev='att'),
    ),
    ],
    setups='tas',  # this is the name of a setup that must be loaded in the
                   # NICOS master instance for this block to be displayed
)

_detectorblock = Block('Detector', [
    BlockRow(
        Field(name='timer', dev='timer'),
        Field(name='ctr1',  dev='ctr1'),
        Field(name='ctr2',  dev='ctr2'),
    ),
    ],
    setups='detector',
)

_tasblock = Block('Triple-axis', [
    BlockRow(
        Field(dev='tas[0]', name='H', format='%.3f', unit=''),
        Field(dev='tas[1]', name='K', format='%.3f', unit=''),
        Field(dev='tas[2]', name='L', format='%.3f', unit=''),
        Field(dev='tas[3]', name='E', format='%.3f', unit=''),
    ),
    BlockRow(
        Field(key='tas/scanmode', name='Mode'),
        Field(dev='mono', name='ki'),
        Field(dev='ana', name='kf'),
        Field(key='tas/energytransferunit', name='Unit'),
    ),
    ],
    setups='tas',
)

_tempblock = Block('Temperature', [
    BlockRow(
        Field(dev='T'),
        Field(key='t/setpoint', name='Setpoint'),
    ),
    BlockRow(
        Field(dev='T', plot='T', plotwindow=300, width=50, height=40),
        Field(key='t/setpoint', name='SetP', plot='T', plotwindow=300),
    ),
    ],
    setups='cryo',
)

_sansblock = Block('SANS (log/lin)', [
    BlockRow(
        Field(name='Data (lin)', picture='live_lin.png', width=24, height=24),
        Field(name='Data (log)', picture='live_log.png', width=24, height=24),
    ),
    ],
    setups='sans',
)

_rightcolumn = Column(_axisblock, _detectorblock, _sansblock)

_leftcolumn = Column(_tasblock, _tempblock)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'NICOS status monitor',
        filename = 'data/status.html',
        loglevel = 'info',
        interval = 3,
        cache = 'localhost:14869',
        prefix = 'nicos/',
        font = 'Helvetica',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [[_expcolumn],
                  [_rightcolumn, _leftcolumn]],
    ),
)
