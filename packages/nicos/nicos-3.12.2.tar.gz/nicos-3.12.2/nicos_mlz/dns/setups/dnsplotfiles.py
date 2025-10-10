description = 'Write files for each measurement'
group = 'optional'

sysconfig = dict(
    datasinks = ['DNSFileSaver', 'YAMLSaver'],
)

devices = dict(
    DNSFileSaver = device('nicos_mlz.dns.devices.dnsfileformat.DNSFileSink',
        detectors = ['det'],
    ),
    YAMLSaver = device('nicos_mlz.dns.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
    ),
)
