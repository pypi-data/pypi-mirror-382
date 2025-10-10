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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

import numpy as np

from nicos.core import Override, Param, Value, floatrange, oneof
from nicos.devices.generic import ScanningDetector as NicosScanDet

from nicos_mlz.reseda.utils import MiezeFit


class ScanningDetector(NicosScanDet):
    """Reseda scanning detector."""

    parameters = {
        'echopoints': Param('Number of echo points',
                            type=oneof(4, 19), default=4, settable=True,
                            userparam=True),
        'echostep': Param('Current difference between points',
                          type=floatrange(0), default=0.1, settable=True,
                          userparam=True),
        'echostart': Param('starting current value for the phase coil',
                           type=float, default=0, userparam=True,
                           settable=True),
    }

    parameter_overrides = {
        'positions': Override(settable=False, volatile=True),
    }

    fitter = MiezeFit()

    def _processDataset(self, dataset):
        for det in dataset.detectors:
            for imgdet in det._attached_images:
                if getattr(imgdet, 'mode', None) == 'image':
                    # extract roi.counts
                    roivalues = []
                    scanvalues = []
                    for subset in dataset.subsets:
                        for i, val in enumerate(subset.detvalueinfo):
                            if val.name.endswith('.roi'):
                                roivalues.append(subset.detvaluelist[i])
                                break
                        scanvalues.append(subset.devvaluelist[0])
                    # ofs, ampl, phase, freq
                    res = self.fitter.run(scanvalues, roivalues, None)
                    if res._failed:
                        self.log.warning(res._message)
                    return [res.avg, res.davg,
                            res.contrast, res.dcontrast,
                            res.phase, res.dphase,
                            res.freq, res.dfreq]
        res = []
        for ctr in self._attached_detector._attached_counters:
            x = []
            y = []
            for subset in dataset.subsets:
                for i, val in enumerate(subset.detvalueinfo):
                    if val.name == ctr.name:
                        y.append(subset.detvaluelist[i])
                        x.append(subset.devvaluelist[0])
                        break
            # ofs, ampl, phase, freq
            res = self.fitter.run(x, y, None)
            if res._failed:
                self.log.warning(res._message)
            res.extend([
                res.avg, res.davg,
                res.contrast, res.dcontrast,
                res.phase, res.dphase,
                res.freq, res.dfreq])
        return res

    def doReadPositions(self):
        return self._calc_currents(self.echopoints, self.echostep,
                                   self.echostart)

    def _calc_currents(self, n, echostep=0.1, startval=0):
        return (startval +
                np.arange(-n // 2 + 1, n // 2 + 1, 1) * echostep).tolist()

    def valueInfo(self):
        res = []
        for imgdet in self._attached_detector._attached_images:
            if getattr(imgdet, 'mode', None) in ['image']:
                return (
                    Value('fit.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('fit.avgErr', unit='', type='error', errors='none',
                          fmtstr='%.1f'),
                    Value('fit.contrast', unit='', type='other', errors='next',
                          fmtstr='%.3f'),
                    Value('fit.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('fit.phase', unit='', type='other', errors='next',
                          fmtstr='%.3f'),
                    Value('fit.phaseErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('fit.freq', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('fit.freqErr', unit='', type='error', errors='none',
                          fmtstr='%.1f'),
                )
        res = []
        for ctr in self._attached_detector._attached_counters:
            res.append(Value('%s.fit.avg' % ctr.name, unit=ctr.unit,
                             type='other', errors='next', fmtstr='%.1f'))
            res.append(Value('%s.fit.avgErr' % ctr.name, unit=ctr.unit,
                             type='error', errors='none', fmtstr='%.1f'))
            res.append(Value('%s.fit.contrast' % ctr.name, unit=ctr.unit,
                             type='other', errors='next', fmtstr='%.3f'))
            res.append(Value('%s.fit.contrastErr' % ctr.name, unit=ctr.unit,
                             type='error', errors='none', fmtstr='%.3f'))
            res.append(Value('%s.fit.phase' % ctr.name, unit=ctr.unit,
                             type='other', errors='next', fmtstr='%.1f'))
            res.append(Value('%s.fit.phaseErr' % ctr.name, unit=ctr.unit,
                             type='error', errors='none', fmtstr='%.1f'))
            res.append(Value('%s.fit.freq' % ctr.name, unit=ctr.unit,
                             type='other', errors='next', fmtstr='%.1f'))
            res.append(Value('%s.fit.freqErr' % ctr.name, unit=ctr.unit,
                             type='error', errors='none', fmtstr='%.1f'))
        return tuple(res)
