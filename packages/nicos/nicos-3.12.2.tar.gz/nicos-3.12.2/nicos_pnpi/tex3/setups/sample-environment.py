description = 'Sample Environment movements'


tango_base = configdata('localconfig.tango_base')

omega_conf = configdata('localconfig.OMEGA_CONF')
phi_conf = configdata('localconfig.PHI_CONF')
chi_conf = configdata('localconfig.CHI_CONF')
theta_conf = configdata('localconfig.THETA_CONF')


devices = dict(
    omega = device('nicos.devices.entangle.Motor',
                   description = omega_conf['description'],
                   tangodevice = tango_base+'device/axis/omega',
                   precision = omega_conf['precision'],
                   visibility = omega_conf['visibility'],
                   abslimits = omega_conf['abslimits'],
                   speed = omega_conf['speed'],
                   unit = omega_conf['unit'],
                   ),
    phi = device('nicos.devices.entangle.Motor',
                 description = phi_conf['description'],
                 tangodevice = tango_base+'device/axis/phy',
                 precision = phi_conf['precision'],
                 visibility = phi_conf['visibility'],
                 abslimits = phi_conf['abslimits'],
                 speed = phi_conf['speed'],
                 unit = phi_conf['unit'],
                 ),
    chi = device('nicos.devices.entangle.Motor',
                 description = chi_conf['description'],
                 tangodevice = tango_base+'device/axis/chi',
                 precision = chi_conf['precision'],
                 visibility = chi_conf['visibility'],
                 abslimits = chi_conf['abslimits'],
                 speed = chi_conf['speed'],
                 unit = chi_conf['unit'],
                 ),
    theta = device('nicos.devices.entangle.Motor',
                   description = theta_conf['description'],
                   tangodevice = tango_base+'device/axis/theta',
                   precision = theta_conf['precision'],
                   visibility = theta_conf['visibility'],
                   abslimits = theta_conf['abslimits'],
                   speed = theta_conf['speed'],
                   unit = theta_conf['unit'],
                   ),
)
