description = 'Setup for the GALAXI status monitor'
group = 'special'

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor for GALAXI.',
        loglevel = 'info',
        cache = 'localhost:14869',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        layout = [Row(Column(Block('Experiment', [
            BlockRow(
                Field(name='Proposal', key='exp/proposal', width=7),
                Field(name='Title', key='exp/title', width=20, istext=True,
                      maxlen=20),
                Field(name='Current status', key='exp/action', width=40,
                      istext=True, maxlen=40),
                Field(name='Last file', key='exp/lastscan'),
            ),
            ],
        ),))],
    ),
)
