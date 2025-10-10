description = 'ThermoJet sample environment'
group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    T_thermojet = device('nicos.devices.entangle.TemperatureController',
        description = 'ThermoJet temperature',
        tangodevice = tango_base + 'thermojet/control',
    ),
    thermojet_airflow = device('nicos.devices.entangle.AnalogOutput',
        description = 'ThermoJet airflow',
        tangodevice = tango_base + 'thermojet/airflow',
    ),
)
