description = 'NE1600 syringe pump'

pv_root = 'E04-SEE-FLUCO:NE1600-001:'

devices = dict(
    pump_status_1600=device(
        'nicos.devices.epics.pva.EpicsStringReadable',
        description='The current pump status',
        readpv='{}STATUS_TEXT'.format(pv_root),
        visibility=(),
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    ),
    syringe_pump_1600=device(
        'nicos_ess.devices.epics.syringe_pump.SyringePumpController',
        description='Single axis positioner',
        status='pump_status_1600',
        start_pv='{}RUN'.format(pv_root),
        stop_pv='{}STOP'.format(pv_root),
        purge_pv='{}PURGE'.format(pv_root),
        pause_pv='{}PAUSE'.format(pv_root),
        message_pv='{}MESSAGE_TEXT'.format(pv_root),
    ),
)
