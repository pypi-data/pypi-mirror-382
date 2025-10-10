# pylint: skip-file

# test: needs = tango
# test: setups = hexapod

pause("Please manually move detector arm in to the direction of the guide (Reibrad switch 1, Air Switch 1). Once finished change Reibrad switch 0.")
pause("Ready to reference detector arm. Continue?")
reference(detarm)
pause("Please manually move omega (table) clock wise in order to reference (Platform switch).")
pause("Ready to reference omega (table)?")
reference(omega)
pause("Move to initial position?")
maw(tx, 0, ty, -4, tz, 0, rz, 0, rx, 0, ry, 0, omega, 0, detarm, 0)
