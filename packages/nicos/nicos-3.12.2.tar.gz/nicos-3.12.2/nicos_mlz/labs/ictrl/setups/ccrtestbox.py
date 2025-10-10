description = 'Devices for the CCR test box'

group = 'optional'

tangohost = 'ictrlsrv.ictrl.frm2.tum.de:10000'

dev_prefix = 'tango://%s/ccrtest/plc' % tangohost

devices = dict(
    tb_v1 = device('nicos.devices.entangle.AnalogOutput',
        description = 'Simulated pressure sensor 1 signal (0-10V)',
        tangodevice = '%s/_v1' % dev_prefix,
        abslimits = (0, 10),
        unit = 'V',
        pollinterval = 5,
        maxage = 6,
    ),
    tb_v2 = device('nicos.devices.entangle.AnalogOutput',
        description = 'Simulated pressure sensor 2 signal (0-10V)',
        tangodevice = '%s/_v2' % dev_prefix,
        abslimits = (0, 10),
        unit = 'V',
        pollinterval = 5,
        maxage = 6,
    ),
    tb_err_gaspressure = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'gas pressure error input to the ccr',
        tangodevice = '%s/_gaspressure_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_err_gastemp = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'gas temperature error input to the ccr',
        tangodevice = '%s/_gastemp_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_err_motortemp = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'motor temperature error input to the ccr',
        tangodevice = '%s/_gastemp_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_err_oil = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'oil temperature error input to the ccr',
        tangodevice = '%s/_oil_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_err_power = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'power fail error input to the ccr',
        tangodevice = '%s/_oil_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_err_waterin = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'water inlet error input to the ccr',
        tangodevice = '%s/_oil_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_err_waterout = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'water outlet error input to the ccr',
        tangodevice = '%s/_oil_err' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'ok': 0,
            'signal_error': 1,
        }
    ),
    tb_state_run = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'running state of the compressor input to the ccr',
        tangodevice = '%s/_runstat_state' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
    tb_warn_solenoid = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'bypass solenoid input to the ccr',
        tangodevice = '%s/_solenoid' % dev_prefix,
        pollinterval = 5,
        maxage = 6,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
    tb_compressor = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from CCR box: Compressor state',
        tangodevice = '%s/_compressor_on' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
    tb_p1power = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from test box: P1 power state',
        tangodevice = '%s/_powerp1_ok' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'ok': 1,
            'failure': 0,
        }
    ),
    tb_gasvalve = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from CCR box: gas valve state',
        tangodevice = '%s/_gasvalve_on' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
    tb_remote = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from CCR box: remote control state',
        tangodevice = '%s/_remote_on' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
    tb_reset = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from CCR box: reset state',
        tangodevice = '%s/_reset_on' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
    tb_p2power = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from test box: P2  power state',
        tangodevice = '%s/_powerp2_ok' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'ok': 1,
            'failure': 0,
        }
    ),
    tb_vacuumvalve = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Feedback from CCR box: vacuum valve state',
        tangodevice = '%s/_vacuumvalve_on' % dev_prefix,
        pollinterval = 1,
        maxage = 2,
        mapping = {
            'on': 1,
            'off': 0,
        }
    ),
)
