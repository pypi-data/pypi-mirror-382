description = 'Sample devices in the SINQ DMC.'

pvprefix = 'SQ:DMC:mcu4:'

no_prefix = 'SQ:DMC:optics:'


devices = dict(
    taz=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Optics Z motor',
               motorpv=f'{no_prefix}taz',
               errormsgpv=f'{no_prefix}taz-MsgTxt',
               ),

    optics_z=device('nicos.devices.epics.pyepics.motor.EpicsMonitorMotor',
              description='Z-motor',
              motorpv=f'{no_prefix}m1',
              ),
    optics_lin=device('nicos.devices.epics.pyepics.motor.EpicsMonitorMotor',
              description='linear stage',
              motorpv=f'{no_prefix}m2',
              ),
    optics_rot=device('nicos.devices.epics.pyepics.motor.EpicsMonitorMotor',
              description='rotation stage',
              motorpv=f'{no_prefix}m3',
              ),
)
