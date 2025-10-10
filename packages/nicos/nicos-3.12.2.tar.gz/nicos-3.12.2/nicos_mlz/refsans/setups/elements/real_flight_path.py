description = 'real flight path'

group = 'lowlevel'

includes = ['detector']

devices = dict(
    real_flight_path = device('nicos_mlz.refsans.devices.resolution.RealFlightPath',
        description = description,
        # visibility = (),
        table = 'det_table',
        pivot = 'det_pivot',
    ),
)
