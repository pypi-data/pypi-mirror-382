# pylint: skip-file

# test: needs = tango
# test: setups = dns

# Typical sample-detector scan going through all field configurations.

N = 1
DET_CENTER = -15.0
SAMPLE_CENTER = 70.

m = list(field.mapping)
m.remove("off")
m.remove("zero field")
for i in range(N):
    for f in m:
        cscan([det_rot, sample_rot], [DET_CENTER, SAMPLE_CENTER], [0.5, 0.2], 10,
              field=f, flipper=['on', 'off'], tsf=20, tnsf=10)
