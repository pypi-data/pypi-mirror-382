description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
#    dict(condition = 'det_kwscounting and '
#                     'abs(selector_speed_value - selector_speed_target) > '
#                     'selector_speed_precision',
#         message = 'Selector outside of target speed, count paused',
#         scriptaction = 'pausecount',
#         gracetime = 10,
#         type = 'default',
#    ),
#    dict(condition = 'det_kwscounting and '
#                     '(abs(chopper_params_value[0] - chopper_params_target[0]) > 0.1 or '
#                     'abs(chopper_params_value[1] - chopper_params_target[1]) > 1)',
#         message = 'Chopper outside of target frequency/phase, count paused',
#         scriptaction = 'pausecount',
#         gracetime = 1,
#         type = 'default',
#    ),
#    dict(condition = 'det_kwscounting and shutter_value != "open"',
#         message = 'Shutter closed, count paused',
#         scriptaction = 'pausecount',
#         gracetime = 1,
#         type = 'default',
#    ),
#    dict(condition = 'det_kwscounting and (sixfold_shutter_value != "open" or '
#                     'nl3b_shutter_value != "open")',
#         message = 'Sixfold or NL3b shutter closed, count paused',
#         scriptaction = 'pausecount',
#         gracetime = 1,
#         type = 'default',
#    ),
#    dict(condition = 'det_kwscounting and '
#                     'abs(t_peltier_value - t_peltier_setpoint) > '
#                     '2 * t_peltier_precision',
#         message = 'Peltier temperature outside of setpoint, count paused',
#         scriptaction = 'pausecount',
#         gracetime = 1,
#         type = 'default',
#         setup = 'peltier',
#    ),
#    dict(condition = 'det_kwscounting and '
#                     'abs(t_julabo_value - t_julabo_setpoint) > '
#                     '2 * t_julabo_precision',
#         message = 'Julabo temperature outside of setpoint, count paused',
#         scriptaction = 'pausecount',
#         gracetime = 1,
#         type = 'default',
#         setup = 'waterjulabo',
#    ),
#    dict(condition = 'det_kwscounting and (chopper1_freq_status[0] == WARN or '
#                     'chopper2_freq_status[0] == WARN)',
#         message = 'Chopper off, but not in parking position',
#         gracetime = 1,
#         type = 'default',
#    ),
]

includes = ['notifiers']

notifiers = {
    'default':  ['email'],
    'critical': ['email', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
