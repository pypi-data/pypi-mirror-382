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

"""NICOS experiment class for KWS1/2."""

import os
import time
from os import path

from nicos.utils import printTable

from nicos_mlz.devices.experiment import Experiment


class KWSExperiment(Experiment):
    """Experiment object customization for KWS."""

    DATA_SUFFIX = '.DAT'
    PROTO_HEADERS = ['Run', 'Sel', 'Coll', 'Det', 'Sample',
                     'TOF', 'Pol', 'Lens', 'Time', 'Cts', 'Rate']
    RUNNO_INDEX = 1
    IGNORE_SENV = ('T', 'Ts')

    def doFinish(self):
        """Automatic protocol generation before finishing a user experiment."""
        if self.proptype != 'user':
            return
        proto_path = path.join(self.proposalpath, 'protocol.txt')
        try:
            text = self._generate_protocol(with_ts=True)
            with open(proto_path, 'w', encoding='utf-8') as fp:
                fp.write(text)
        except Exception:
            self.log.warning('Error during protocol generation', exc=1)
        else:
            self.log.info('Protocol generated at %s', proto_path)

    def _generate_protocol(self, first=None, last=None, with_ts=False):
        data = []
        senv = set()

        for fname in os.listdir(self.datapath):
            if not fname.endswith(self.DATA_SUFFIX):
                continue
            parts = fname.split('_')
            if not (len(parts) > 1 and parts[self.RUNNO_INDEX].isdigit()):
                continue
            runno = int(parts[self.RUNNO_INDEX])
            if first is not None and runno < first:
                continue
            if last is not None and runno > last:
                continue
            try:
                data.append(self._read_data_file(
                    runno, senv, path.join(self.datapath, fname)))
            except Exception as err:
                self.log.warning('could not read %s: %s', fname, err)
                continue
        data.sort(key=lambda x: x['#'])

        headers = self.PROTO_HEADERS[:]
        if with_ts:
            headers.insert(1, 'Started')
        for sename in sorted(senv):
            if sename not in self.IGNORE_SENV:
                headers.append(sename)
        items = []
        day = ''
        for info in data:
            if 'Sample' not in info:
                continue
            if with_ts and info['Day'] != day:
                day = info['Day']
                items.append([''] * len(headers))
                items.append(['', day] + [''] * (len(headers) - 2))
            items.append([info.get(key, '') for key in headers])

        lines = ['Protocol for proposal %s, generated on %s' %
                 (self.proposal, time.strftime('%Y-%m-%d %H:%M')),
                 '']
        printTable(headers, items, lines.append)
        return '\n'.join(lines) + '\n'

    def _read_data_file(self, runno, senv, fname):
        return read_dat_file(runno, senv, fname)


def read_dat_file(runno, senv, fname):
    data = {'#': runno, 'Run': str(runno), 'TOF': 'no'}
    with open(fname, encoding='utf-8') as it:
        for line in it:
            if line.startswith('Standard_Sample '):
                parts = line.split()
                data['Day'] = parts[-2]
                data['Started'] = parts[-1][:-3]
            elif line.startswith('(* Comment'):
                next(it)
                data['Sel'] = next(it).split('|')[-1].strip()[7:]
                data['Sample'] = next(it).split('|')[0].strip()
            elif line.startswith('(* Collimation'):
                next(it)
                next(it)
                info = next(it).split()
                data['Coll'] = info[0] + 'm'
                data['Pol'] = info[4]
                data['Lens'] = info[5]
                if data['Lens'] == 'out-out-out':
                    data['Lens'] = 'no'
            elif line.startswith('(* Detector Discription'):
                for _ in range(3):
                    next(it)
                info = next(it).split()
                data['Det'] = '%.3gm' % float(info[1])
            elif line.startswith('(* Temperature'):
                for _ in range(4):
                    info = next(it)
                    if 'dummy' in info:
                        continue
                    parts = info.split()
                    data[parts[0]] = parts[3]
                    senv.add(parts[0])
            elif line.startswith('(* Real'):
                data['Time'] = next(it).split()[0] + 's'
                data['t'] = int(data['Time'][:-1])
            elif line.startswith('(* Detector Data Sum'):
                next(it)
                total = float(next(it).split()[0])
                data['Cts'] = '%.2g' % total
                data['Rate'] = '%.0f' % (total / data['t'])
            elif line.startswith('(* Chopper'):
                data['TOF'] = 'TOF'
            elif line.startswith('(* Detector Time Slices'):
                if data['TOF'] != 'TOF':
                    data['TOF'] = 'RT'
            elif line.startswith('(* Detector Data'):
                break
    return data
