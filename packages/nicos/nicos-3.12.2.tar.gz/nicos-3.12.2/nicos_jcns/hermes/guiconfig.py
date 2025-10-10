"""HERMES NICOS GUI configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            hsplit(
                vsplit(
                    panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel'),
                    panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
                ),
            ),
            tabbed(
                ('All output', panel(
                    'nicos.clients.gui.panels.console.ConsolePanel',
                    hasinput=False, hasmenu=False
                )),
                ('Errors/Warnings', panel(
                    'nicos.clients.gui.panels.errors.ErrorPanel'
                )),
            ),
        ),
        ('Experiment Info', panel(
            'nicos.clients.gui.panels.expinfo.ExpInfoPanel', dockpos='left',
        )),
        ('NICOS devices', panel(
            'nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
            dockpos='right',
        )),
    )),
    ('Script Editor', vsplit(
        panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
        panel('nicos.clients.gui.panels.editor.EditorPanel'),
    )),
    ('Live data', panel(
        'nicos.clients.gui.panels.live.LiveDataPanel', instrument='HERMES',
        detectors=['counters'],
    )),
    ('Scan Plotting', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    ('Device Plotting', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    ('Logbook', panel('nicos.clients.gui.panels.elog.ELogPanel')),
)

windows = []

tools = [
    cmdtool('Server control (Marche)', 'marche-gui'),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=True),
]
