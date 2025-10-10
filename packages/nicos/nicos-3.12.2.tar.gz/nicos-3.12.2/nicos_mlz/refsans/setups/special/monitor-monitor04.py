description = 'Sample Environment and Miscellaneous [Monitor 04]'
group = 'special'

_tempcol = Column(
    Block('Julabo Thermostat Status', [
        BlockRow(
            Field(name='temperature ', dev='julabo_temp', width=10,  format='%.2f', unit='(\u2103)'),
            Field(name='target temperature ', key='julabo_temp/target', width=10,  format='%.2f', unit='(\u2103)'),
            Field(name='target temperature ', key='julabo_temp.target', width=10,  format='%.2f', unit='(\u2103)'),
            Field(name='internal bath temperature ', dev='julabo_int', width=10,  format='%.2f', unit='(\u2103)'),
            Field(name='external sensor temperature ', dev='julabo_ext', width=10,  format='%.2f', unit='(\u2103)'),
            Field(name='external sensor flow ', dev='julabo_flow', width=10,  format='%.1f', unit='(L/min)'),
            # Field(name='Cryostat', dev='temp_cryo', width=14, unit='(K)'),
        ),
        ],
        setups = 'julabo',
    ),
)

_julabo_plot = Column(
    Block('Temperature history', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=60, height=30, plotwindow=1800,
                  devices=['julabo_temp/target','julabo_ext', 'julabo_int'],
                  names=['T set 30min','T ext 30min', 'T int 30 min'],
                  legend=True),
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=60, height=30, plotwindow=12*3600,
                  devices=['julabo_temp/target','julabo_ext', 'julabo_int'],
                  names=['T set 12h','T ext 12h', 'T int 12h'],
                  legend=True),
        ),
        ],
        setups = 'julabo',
    ),
)

_syringepumps = Column(
    Block('Syringe Pumps Status', [
        BlockRow(
            Field(name='[Pump 0] syringe diameter', dev='pump0_diameter', width=10, format='%.2f', unit='(mm)'),
            Field(name='[Pump 0] injection/withdraw flux', dev='pump0_rate', width=10, format='%.2f', unit='(ml/min)'),
            Field(name='[Pump 0] volume injected/withdrawn', dev='pump0_run', width=10, format='%.2f', unit='(ml)'),
        ),
        BlockRow(
            Field(name='[Pump 1] syringe diameter', dev='pump1_diameter', width=10, format='%.2f', unit='(mm)'),
            Field(name='[Pump 1] injection/withdraw flux', dev='pump1_rate', width=10, format='%.2f', unit='(ml/min)'),
            Field(name='[Pump 1] volume injected/withdrawn', dev='pump1_run', width=10, format='%.2f', unit='(ml)'),
        ),
        ],
        setups = 'syringe01',
    ),
)

_nima = Column(
    Block('Langmuir Trough Status', [
        BlockRow(
            Field(name='area surface', dev='nima_area', width=10, format='%.1f', unit='(cm\u00b2)'),
            Field(name='pressure', dev='nima_pressure', width=10, format='%.2f', unit='(mN/m)'),
            Field(name='barrier speed', dev='nima_speed', width=10, format='%.2f', unit='(mm/s)'),
            Field(name='Gonio Z', dev='gonio_z', width=10, format='%.2f', unit='(mm)'),
            Field(name='height', dev='height', width=10, format='%.2f', unit='(mm)'),
        ),
        ],
        setups = 'nima',
    ),
)

_ubahn = Column(
    Block('U6 Subway to Klinikum Gro\u00dfhadern', [
        BlockRow(
                 Field(name='Next trips in', dev='Ubahn', istext=True, unit = 'min'),
        ),
        ],
    ),
)

#_flipper = Column(
#    Block('Spin Flipper', [
#        BlockRow(
#            Field(dev='frequency', width=7, unit='(kHz)'),
#            Field(dev='current', width=7, unit='(A)'),
#            Field(dev='flipper', name='Flipping_State', width=7),
#        ),
#        ],
#    ),
#)


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_tempcol ),
            Row(_julabo_plot),
            Row(_syringepumps),
            Row(_nima),
            Row(_ubahn),
        ],
    ),
)
