description = 'Selector area slit setup'
group = 'lowlevel'
display_order = 22

excludes = ['virtual_resolution']

res_presets = configdata('config_resolution.RESOLUTION_PRESETS')

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    resolution = device('nicos_mlz.kws3.devices.resolution.Resolution',
        description = 'select resolution presets',
        blockingmove = False,
        moveables = [
            'sel_ap2_x_left', 'sel_ap2_x_right', 'sel_ap2_y_lower',
            'sel_ap2_y_upper', 'det_x', 'det_y', 'det_z'
        ],
        mapping = {
            k: list(v['ap']) + [v['det_x'], v['det_y'], v['det_z']]
            for (k, v) in res_presets.items()
        },
        fallback = 'unknown',
        precision = [0.1, 0.1, 0.1, 0.1, 0.01, 0.01, 0.01],
        presets = res_presets,
    ),
    sel_ap1 = device('nicos.devices.generic.TwoAxisSlit',
        description = 'aperture before selector',
        fmtstr = '%.3f x %.3f',
        horizontal = 'sel_ap1_width',
        vertical = 'sel_ap1_height',
        parallel_ref = True,
        visibility = (),
    ),
    sel_ap1_width = device('nicos.devices.entangle.Motor',
        description = 'aperture selector horizontal opening',
        tangodevice = s7_motor + 'sel_ap1_x_delta',
        unit = 'mm',
        precision = 0.01,
        visibility = (),
    ),
    sel_ap1_height = device('nicos.devices.entangle.Motor',
        description = 'aperture selector vertical opening',
        tangodevice = s7_motor + 'sel_ap1_y_delta',
        unit = 'mm',
        precision = 0.01,
        visibility = (),
    ),
    sel_ap2 = device('nicos.devices.generic.Slit',
        description = 'selector jj-xray aperture',
        coordinates = 'opposite',
        opmode = 'offcentered',
        fmtstr = '(%.2f, %.2f) %.2f x %.2f',
        left = 'sel_ap2_x_left',
        right = 'sel_ap2_x_right',
        bottom = 'sel_ap2_y_lower',
        top = 'sel_ap2_y_upper',
        parallel_ref = True,
    ),
    sel_ap2_x_left = device('nicos.devices.entangle.Motor',
        description = 'selector jj-xray aperture left',
        tangodevice = s7_motor + 'sel_ap2_x_left',
        unit = 'mm',
        precision = 0.1,
        visibility = (),
    ),
    sel_ap2_x_right = device('nicos.devices.entangle.Motor',
        description = 'selector jj-xray aperture right',
        tangodevice = s7_motor + 'sel_ap2_x_right',
        unit = 'mm',
        precision = 0.1,
        visibility = (),
    ),
    sel_ap2_y_upper = device('nicos.devices.entangle.Motor',
        description = 'selector jj-xray aperture upper',
        tangodevice = s7_motor + 'sel_ap2_y_upper',
        unit = 'mm',
        precision = 0.1,
        visibility = (),
    ),
    sel_ap2_y_lower = device('nicos.devices.entangle.Motor',
        description = 'selector jj-xray aperture lower',
        tangodevice = s7_motor + 'sel_ap2_y_lower',
        unit = 'mm',
        precision = 0.1,
        visibility = (),
    ),
)

extended = dict(
    poller_cache_reader = ['det_x', 'det_y', 'det_z'],
    representative = 'resolution',
)

alias_config = {
    'sam_ap': {'sel_ap2': 80},
}
