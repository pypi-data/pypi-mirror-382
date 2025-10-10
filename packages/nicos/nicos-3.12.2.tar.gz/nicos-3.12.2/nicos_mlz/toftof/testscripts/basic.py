# pylint: skip-file

# test: needs = tango
# test: subdirs = frm2
# test: setups = toftof
# test: setupcode = SetDetectors(det)
# test: needs = h5py

# read some special devices

read(chSpeed)
read(chWL)
read(chRatio)

read(slit)
read(ngc)
read(rc_onoff)


# test count

count(200)
