description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    # dict(condition = 'cooltemp_value > 30',
    #      message = 'Cooling water temperature exceeds 30C, check FAK40 or MIRA Leckmon!',
    #      type = 'critical',
    # ),
    dict(condition = 'befilter_value != \'unused\' and TBeFilter_value > 80 and TBeFilter_value < 1000',
         message = 'Be filter temperature > 80 K, check cooling!',
         gracetime = 30,
         type = 'critical',
         setup = 'befilter',
    ),
    dict(condition = 'befilter_value != \'unused\' and TBeFilter_value > 1000',
         message = 'Be filter thermometer disconnected',
         gracetime = 600,
         setup = 'befilter',
    ),
    dict(condition = 'water_value != "on"',
         message = 'WATER is not flowing',
         gracetime = 5,
         type = 'critical',
         setup = 'water',
    ),
    dict(condition = 'T_value > 1.9 and T_setpoint < 1.9',
         message = 'Cooling of JVM is not enough!!! Ts > 1.9K.',
         gracetime = 20,
         type = 'default',
         setup = 'wm5v',
    ),
#    dict(condition = 'T_ccm12v_vti_value > 2.0',
#         message = 'VTI temperature over 2K',
#         type = 'onlyastrid',
#         scriptaction = 'pausecount',
#         setup = 'ccm12v',
#    ),
    # dict(condition = 'sgy_fixedby != None and abs(sgy_target - sgy_value) > 0.1',
    #      message = 'SGY moved without reason, trying to fix automatically!',
    #      gracetime = 2,
    #      type = 'critical',
    #      action = 'release(sgy);maw(sgy,sgy.target);fix(sgy)'
    # ),
    # dict(condition = 'sgx_fixedby != None and abs(sgx_target - sgx_value) > 0.1',
    #      message = 'SGX moved without reason, trying to fix automatically!',
    #      gracetime = 2,
    #      type = 'critical',
    #      action = 'release(sgx);maw(sgx,sgx.target);fix(sgx)'
    # ),
    # dict(condition = 'T_heaterpower < 0.000001 and T_setpoint > 0.5',
    #      message = 'PROBLEM with heater - not heating - check PANDA',
    #      gracetime = 300,
    #      type = 'onlypetr',
    #      setup = 'cci3he03',
    # ),
    # dict(condition = 'T_heaterpower > 0.002',
    #      message = 'PROBLEM with heater - heating too much - check PANDA',
    #      gracetime = 300,
    #      type = 'onlypetr',
    #      setup = 'cci3he03',
    # ),
]

includes = ['notifiers']

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'phys.panda.frm2',
        notifiers = {
            'default': ['email1'],
            'critical': ['email1', 'smser'],
            'onlyastrid': ['email2', 'smsastr'],
        },
        watch = watch_conditions,
        mailreceiverkey = 'email/receivers',  ## replace all email addresses with MailRecievers from current experiment
        #mailreceiverkey = '',   ## normal settings
        loglevel = 'debug',
    ),
)
