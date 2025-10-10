description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/watchdog/#watch-conditions
watch_conditions = [
    dict(
        condition = 'len(Exp_scripts) > 0 and  emergency_value == 1',
        message = 'Emergency stop engaged: FULL STOP!!!!',
        gracetime = 0,
        type = 'critical',
        scriptaction = 'immediatestop',
    ),
    dict(
        condition = 'vs_speed_value > 5 and vs_vibration_value == 0',
        setup = 'velocity_selector',
        message = 'Excessive vibration of velocity selector!! STOPPING VS!!',
        gracetime = 1,
        type = 'critical',
        action = 'maw(vs_speed, 0)'
    ),
]

notifiers = {}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
