# pylint: skip-file

# test: subdirs = frm2
# test: setups = bruker_axs,pilatus_det,pindiodes
# test: setupcode = SetDetectors(pilatus)
# test: skip

# sample scan with pilatus and pindioden

SetDetectors(pilatus, singledetectors)
move(shutter, 'open')
maw(pz, -15.0)
scan(pz, [-12.3, -8.2, -4.2, -0.2, 3.8, 7.8, 11.7, 15.8, 19.5], t=10)
move(shutter, 'closed')
maw(prefz, 40.0)
SetDetectors(singledetectors)
move(pindiodesample_move, 'in')
move(shutter, 'open')
scan(pz, -15, 0.1, 401, t=1)
move(shutter, 'closed')
move(pindiodesample_move, 'out')
