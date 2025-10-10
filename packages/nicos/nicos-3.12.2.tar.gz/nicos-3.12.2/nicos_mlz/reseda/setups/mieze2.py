description = 'RESEDA MIEZE setup with resedacascade2 detector (7 foils)'
group = 'basic'
includes = [
    'reseda', 'det_cascade2', 'arm_1', 'armcontrol', 'attenuators',
    'slitsng', 'tuning'
]

startupcode = '''
Exp.measurementmode = 'mieze'
'''
