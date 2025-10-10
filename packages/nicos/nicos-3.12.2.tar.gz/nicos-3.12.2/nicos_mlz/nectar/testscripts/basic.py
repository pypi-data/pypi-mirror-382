# pylint: skip-file

# test: needs = tango
# test: needs = astropy
# test: setups = nectar, servostar, detector
# test: setupcode = SetDetectors(det)

FinishExperiment()
NewSample('Test_abc')
Remark('Collimator 40x50mm')

# Not enough space in y direction, also for x required
maw(sty, 1)
maw(stx, 1)

# take openbeam
for i in range(2):
    openbeamimage(t=1)

# since nectar has no shutter control, this is usually done at the beginning of
# the measurement without sample in beam
for i in range(2):
    darkimage(t=1)

print('OB and DI Finished')

maw(stx, 20)
maw(sty, 10)
tomo(10, sry, t=1)

print('Tomo Finished!')
print('Test finished')
