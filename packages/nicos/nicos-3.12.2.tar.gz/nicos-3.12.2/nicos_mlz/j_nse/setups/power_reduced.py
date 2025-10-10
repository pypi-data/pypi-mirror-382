description = 'power supplies'

group = 'optional'
excludes = ['power']

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    temp_rack1 = device('nicos.devices.entangle.Sensor',
        description = 'PSU Temperature in Rack 1',
        tangodevice = tango_base + 'supply_temp/pow02',
        unit = 'degC',
    ),
    temp_rack2 = device('nicos.devices.entangle.Sensor',
        description = 'PSU Temperature in Rack 2',
        tangodevice = tango_base + 'supply_temp/pow23',
        unit = 'degC',
    ),
)

supplies = list(range(1, 39))
supplies.remove(5)
supplies.remove(33)
for i in range(9, 13):
    supplies.remove(i)
for i in supplies:
    name = 'pow%02d' % i
    devices[name] = \
        device('nicos.devices.entangle.PowerSupply',
               description = 'Power Supply Port %02d' % i,
               tangodevice = tango_base + 'supply/' + name,
               unit = 'A',
              )
