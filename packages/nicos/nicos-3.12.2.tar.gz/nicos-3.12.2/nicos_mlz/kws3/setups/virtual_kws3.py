description = 'Fully virtual KWS-3 setup'
group = 'basic'

modules = ['nicos_mlz.kws3.commands']

includes = [
    'virtual_sample',
    'virtual_selector',
    'virtual_detector',
    'virtual_polarizer',
    'virtual_daq',
]
