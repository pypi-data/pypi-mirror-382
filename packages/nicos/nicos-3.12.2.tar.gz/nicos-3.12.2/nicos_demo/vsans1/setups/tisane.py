description = 'tisane setup for SANS1'

group = 'basic'

modules = ['nicos_mlz.sans1.commands']

includes = ['collimation', 'detector', 'sample_table', 'det1',
            'pressure', 'selector_tower', 'memograph',
            'manual',
            # 'guidehall',
            'outerworld', 'pressure_filter',
            'slit',
            # 'nl4a',
            'flipbox', 'tisane_multifg',  # for setfg and tcount
            # 'frequency',
            'tisane_det',
           ]

excludes = ['sans1']
