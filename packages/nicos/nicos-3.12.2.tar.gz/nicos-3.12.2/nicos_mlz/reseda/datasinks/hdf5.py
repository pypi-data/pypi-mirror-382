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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from time import localtime, strftime, time as currenttime

import h5py
import numpy

from nicos.core import DataSinkHandler, Override, Param
from nicos.core.constants import SCAN, SUBSCAN
from nicos.core.data.sink import DataFileBase
from nicos.devices.datasinks import FileSink
from nicos.utils import toAscii


class HDF5DataFile(DataFileBase, h5py.File):
    def __init__(self, shortpath, filepath):
        DataFileBase.__init__(self, shortpath, filepath)
        h5py.File.__init__(self, filepath, 'w')

        self.subscan_group_tmpl = '%(subscancounter)d'
        self.scalars_tmpl = '%(pointcounter)d'
        self.image_tmpl = '%(pointcounter)d'

        self._subscancounter = 0
        self._current_group = None

    def beginSubscan(self):
        """Creates a hdf5 group/directory for the next echo subscan."""

        subst = {'subscancounter': self._subscancounter}

        self._current_group = self.create_group(
            self.subscan_group_tmpl % subst)
        self._subscancounter += 1

        return self._current_group

    def createScalarsDataset(self, number, data):
        subst = {'pointcounter': number}

        return self._current_group.create_dataset(self.scalars_tmpl
                                                  % subst, data=data)

    def createImageDataset(self, number, data):
        subst = {'pointcounter': number}

        return self._current_group.create_dataset(self.image_tmpl
                                                  % subst, data=data)


class HDF5SinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)

    @property
    def current_file(self):
        return self.sink._current_scan_file

    @current_file.setter
    def current_file(self, value):
        self.sink._current_scan_file = value

    def prepare(self):
        if self.dataset.settype == SUBSCAN:
            self.current_file.beginSubscan()
        elif self.dataset.settype == SCAN:
            self.log.debug('New scan dataset recognized, creating new file')

            self.manager.assignCounter(self.dataset)
            self.sink._current_scan_file = self.manager.createDataFile(
                self.dataset, self.sink.filenametemplate, self.sink.subdir,
                fileclass=HDF5DataFile)
            self.current_file.subscan_group_tmpl = self.sink.subscangrouptmpl
            self.current_file.scalars_tmpl = self.sink.scalarstmpl
            self.current_file.image_tmpl = self.sink.imagetmpl

    def addSubset(self, subset):
        if self.dataset.settype == SCAN:
            return  # outer scan; nothing to do

        if not subset.results:
            return  # no results

        detector = subset.detectors[0]
        data = subset.results[detector.name]  # only 1 detector supported

        # data[1]: image (mieze), data[0]: count sums (nrse)

        if data[0]:
            scalars = numpy.array(data[0], dtype=numpy.int32)
            # begin point counter at 0
            hdf5dataset = self.current_file.createScalarsDataset(
                subset.number - 1, scalars)

            for i, info in enumerate(detector.valueInfo()):
                for attr in ['name', 'type', 'unit']:
                    hdf5dataset.attrs['value_info_%d/%s'
                                      % (i, attr)] = getattr(info, attr)
            self._addMetadata(subset.metainfo, hdf5dataset)
        if data[1]:
            image = numpy.array(data[1][0], dtype=numpy.int32)
            self.current_file.createImageDataset(subset.number - 1, image)

        self.current_file.flush()

    def end(self):
        if self.dataset.settype == SCAN:
            if self.current_file:
                self.log.debug('Finished scan dataset recognized, closing file')
                self.current_file.close()
                self.current_file = None

    def _addMetadata(self, metadata, hdf5dataset):
        hdf5dataset.attrs['begintime'] = strftime(
            '%Y-%m-%d %H:%M:%S', localtime(self.dataset.started))
        hdf5dataset.attrs['endtime'] = strftime(
            '%Y-%m-%d %H:%M:%S', localtime(currenttime()))

        for (dev, param), (_, strvalue, unit, _) in metadata.items():
            hdf5dataset.attrs['%s/%s' % (dev, param)] = \
                toAscii('%s %s' % (strvalue, unit)).strip()


class HDF5Sink(FileSink):
    parameters = {
        'subscangrouptmpl': Param('Name of the sub scan specific group',
                                  type=str, default='echo_%(subscancounter)d'),
        'scalarstmpl': Param('Name of the scalars dataset', type=str,
                             default='scalars_%(pointcounter)d'),
        'imagetmpl': Param('Name of the image dataset', type=str,
                           default='image_%(pointcounter)d'),
    }

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(scancounter)08d.hdf5']),
        'settypes': Override(default=[SCAN, SUBSCAN]),
    }

    handlerclass = HDF5SinkHandler

    def doInit(self, mode):
        self._current_scan_file = None

    def isActive(self, dataset):
        if dataset.settype != SCAN and self._current_scan_file is None:
            return False
        return FileSink.isActive(self, dataset)
