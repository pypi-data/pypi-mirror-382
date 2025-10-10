"""NICOS GUI configuration for PANDA."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('nicos.clients.gui.panels.watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True, dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
           sample_panel=panel('nicos.clients.gui.panels.setup_panel.TasSamplePanel'),
          )
    ),
)

windows = [
    window('Editor', 'editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel',
                  modules=['nicos.clients.gui.cmdlets.qscan'],
                  ),
            panel('nicos.clients.gui.panels.editor.EditorPanel'),
              )),
    window('Scans', 'plotter', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table', panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table', panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors', panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Camera', 'live', panel('nicos.clients.gui.panels.live.LiveDataPanel')),
    window('Pandora', 'editor', panel('nicos_mlz.panda.gui.mtt_manual.MTTManualPanel')),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         sender='panda@frm2.tum.de'),
    tool('Sample environment logbooks',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://wiki.frm2.tum.de/se:jcns:log:index'),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button', 'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
    cmdtool('Marche (Server control)', 'marche-gui'),
    cmdtool('Ana Block control', ['sh', '-c', 'quango-mlzgui -m panda/analyzer/plc_block{1,2,3,4,5} + '
                                  'panda/analyzer/plc_block{6,7,8,9,10} + '
                                  'panda/analyzer/plc_block{11,12,13,14,15} + '
                                  'panda/analyzer/plc_block{16,17,18}']),
]
