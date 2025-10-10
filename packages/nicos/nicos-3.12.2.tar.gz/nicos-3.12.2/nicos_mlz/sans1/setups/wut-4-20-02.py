description = 'W&T Box * 4-20mA * Nr. 2'

_wutbox_dev = setupname.replace('-','_')

devices = {
    f'{_wutbox_dev}_1': device('nicos_mlz.sans1.devices.wut.WutReadValue',
        hostname = f'{setupname}.sans1.frm2.tum.de',
        port = 1,
        description = 'input 1 current',
        fmtstr = '%.3F',
        loglevel = 'info',
        pollinterval = 5,
        maxage = 20,
        unit = 'A',
    ),
    f'{_wutbox_dev}_2': device('nicos_mlz.sans1.devices.wut.WutReadValue',
        hostname = f'{setupname}.sans1.frm2.tum.de',
        port = 2,
        description = 'input 2 current',
        fmtstr = '%.3F',
        loglevel = 'info',
        pollinterval = 5,
        maxage = 20,
        unit = 'A',
    ),
}

monitor_blocks = dict(
    default = Block(f'{setupname}', [
        BlockRow(
            Field(name='input 1', dev=f'{_wutbox_dev}_1'),
            Field(name='input 2', dev=f'{_wutbox_dev}_2'),
        ),
        ],
        setups=setupname,
    ),
)
