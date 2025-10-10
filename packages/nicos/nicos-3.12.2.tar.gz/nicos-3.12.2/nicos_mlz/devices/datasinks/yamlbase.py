# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Base classes for YAML based datasinks."""

from datetime import datetime
from time import time as currenttime

import quickyaml

from nicos import session
from nicos.core import NicosError
from nicos.devices.datasinks.image import SingleFileSinkHandler
from nicos.utils import AutoDefaultODict


def nice_datetime(dt):
    if isinstance(dt, float):
        dt = datetime.fromtimestamp(dt)
    rounded = dt.replace(microsecond=0)
    return rounded.isoformat()


class YAMLBaseFileSinkHandler(SingleFileSinkHandler):

    filetype = 'MLZ.YAML'  # to be overwritten in derived classes
    max_yaml_width = 120
    accept_final_images_only = True
    yaml_array_handling = quickyaml.ARRAY_AS_SEQ

    objects = ['angle', 'clearance', 'current', 'displacement', 'duration',
               'energy', 'frequency', 'temperature', 'wavelength',
               'offset', 'width', 'height', 'length']
    units = ['deg', 'mm', 'A', 'mm', 's', 'meV', 'hertz', 'K', 'A',
             'mm', 'mm', 'mm', 'mm']

    def _readdev(self, devname, mapper=lambda x: x):
        try:
            return mapper(session.getDevice(devname).read())
        except NicosError:
            return None

    def _devpar(self, devname, parname, mapper=lambda x: x):
        try:
            return mapper(getattr(session.getDevice(devname), parname))
        except NicosError:
            return None

    def _dict(self):
        return AutoDefaultODict()

    def _flowlist(self, *args):
        return quickyaml.flowlist(*args)

    def writeData(self, fp, image):
        """Save in YAML format."""
        fp.seek(0)

        expdev = session.experiment
        instrdev = session.instrument

        o = AutoDefaultODict()
        instr = o['instrument']
        instr['name'] = instrdev.instrument
        instr['facility'] = instrdev.facility
        instr['operator'] = ', '.join(instrdev.operators)
        instr['website'] = instrdev.website
        instr['references'] = [AutoDefaultODict({'doi': instrdev.doi})]

        o['format']['identifier'] = self.__class__.filetype
        for obj, unit in zip(self.objects, self.units):
            o['format']['units'][obj] = unit

        exp = o['experiment']
        exp['number'] = expdev.propinfo.get('session', expdev.proposal)
        exp['proposal'] = expdev.proposal
        exp['title'] = expdev.title

        exp['authors'] = []
        for user in expdev.propinfo.get('users', []):
            a = AutoDefaultODict()
            a['name'] = user['name']
            a['affiliation'] = user.get('affiliation')
            a['roles'] = self._flowlist(['principal_investigator'])
            exp['authors'].append(a)
        for user in expdev.propinfo.get('localcontacts', []):
            a = AutoDefaultODict()
            a['name'] = user['name']
            a['affiliation'] = user.get('affiliation')
            a['roles'] = self._flowlist(['local_contact'])
            exp['authors'].append(a)

        meas = o['measurement']
        meas['number'] = self.dataset.number
        meas['unique_identifier'] = '%s/%s/%s' % (
            expdev.proposal, self.dataset.counter, self.dataset.number)

        hist = meas['history']
        hist['started'] = nice_datetime(self.dataset.started)
        hist['stopped'] = nice_datetime(currenttime())

        sample = meas['sample']['description']
        sample['name'] = expdev.sample.samplename

        env = meas['sample']['environment'] = []
        stats = self.dataset.valuestats
        for (info, val) in zip(self.dataset.envvalueinfo,
                               self.dataset.envvaluelist):
            entry = self._dict()
            entry['name'] = info.name
            entry['unit'] = info.unit
            entry['value'] = val
            if info.name in stats:
                entry['mean'] = stats[info.name][0]
                entry['stddev'] = stats[info.name][1]
                entry['min'] = stats[info.name][2]
                entry['max'] = stats[info.name][3]
            env.append(entry)

        self._write_instr_data(meas, image)

        quickyaml.Dumper(width=self.max_yaml_width,
                         array_handling=self.yaml_array_handling).dump(o, fp)
        fp.flush()

    def _write_instr_data(self, meas, image):
        raise NotImplementedError('implement _write_instr_data')
