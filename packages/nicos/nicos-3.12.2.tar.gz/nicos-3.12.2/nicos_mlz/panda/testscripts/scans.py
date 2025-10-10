# pylint: skip-file

# test: needs = tango
# test: subdirs = frm2
# test: setups = panda, sat
# test: setupcode = SetDetectors(det)

sat(2)
qscan((1, 1, 0, -0.5), (0, 0, 0, 0.2), 21, t=2, kf=1.57)
sat(6)
qscan((1, 1, 0, -0.5), (0, 0, 0, 0.2), 21, t=2, kf=1.45)
sat(0)
