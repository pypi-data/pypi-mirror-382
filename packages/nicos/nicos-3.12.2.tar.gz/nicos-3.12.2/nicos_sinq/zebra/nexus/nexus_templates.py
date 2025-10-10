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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import copy

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, ImageDataset, NXAttribute, NXLink, \
    NXScanLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import ArrayParam, CellArray, \
    FixedArray, SaveSampleEnv
from nicos_sinq.sxtal.instrument import EulerSXTal


class ZEBRATemplateProvider(NexusTemplateProvider):
    _zebra_default = {'NeXus_Version': '4.3.0', 'instrument': 'ZEBRA',
                      'owner': DeviceAttribute('ZEBRA', 'responsible'),
                      'entry1:NXentry': {'title': DeviceDataset('Exp',
                                                                'title'),
                                         'proposal_title':
                                             DeviceDataset('Exp', 'title'),
                                         'proposal_id':
                                             DeviceDataset('Exp', 'proposal'),
                                         'start_time': NXTime(),
                                         'zebra_mode':
                                             DeviceDataset('zebramode',
                                                           dtype='string'),
                                         'end_time': NXTime(), 'user:NXuser': {
                                         'name': DeviceDataset('Exp', 'users'),
                                         'email':
                                             DeviceDataset('Exp',
                                                           'localcontact'),
                                         },
                                         'comment':
                                             DeviceDataset('Exp',
                                                           'remark'),
                                         'control:NXmonitor': {
                                             'mode': DetectorDataset('mode',
                                                                     'string'),
                                             'Monitor': DetectorDataset(
                                                 'monitorval', 'float32',
                                                 units=NXAttribute('counts',
                                                                   'string')),
                                             'preset':
                                                 DetectorDataset('preset',
                                                                 'float32'),
                                             'time': DetectorDataset(
                                                 'elapsedtime', 'float32',
                                                 units=NXAttribute('seconds',
                                                                   'string')),
                                         },
                                         'proton_beam:NXmonitor': {
                                             'data': DetectorDataset(
                                                 'protoncurr',
                                                 'int32',
                                                 units=NXAttribute(
                                                     'counts',
                                                     'string'))},
                                         'beam_monitor:NXmonitor': {
                                             'data': DetectorDataset(
                                                 'monitorval',
                                                 'int32',
                                                 units=NXAttribute('counts',
                                                                   'string'))},
                                         'area_detector2:NXdata': {
                                             'data': NXLink(
                                                 '/entry1/ZEBRA/'
                                                 'area_detector2/data'),
                                             'None': NXScanLink(),
                                         },
                                         },
                      }
    _zebra_instrument = {
        'SINQ:NXsource': {
            'name': ConstDataset('SINQ @ PSI', 'string'),
            'type': ConstDataset('Continuous flux spallation source',
                                 'string')
        },
        'collimator_before_mono:NXcollimator': {
            'cex1': DeviceDataset('cex1', units=NXAttribute('degree',
                                                            'string')),
            'cex2': DeviceDataset('cex2', units=NXAttribute('degree',
                                                            'string')),
        },
        'monochromator:NXmonochromator': {
            'description': ConstDataset('PG monochromator', 'string'),
            'wavelength': DeviceDataset('wavelength'),
            'mexz': DeviceDataset('mexz'),
            'mcvl': DeviceDataset('mcvl'),
            'mgvl': DeviceDataset('mgvl'),
            'mgvu': DeviceDataset('mgvu'),
            'theta': DeviceDataset('moml'),
            'two_theta': ConstDataset(40.2, 'float',
                                      unit=NXAttribute('degree', 'string')),
        },
        'slits_s1:NXslit': {
            'top': DeviceDataset('s1vt'),
            'bottom': DeviceDataset('s1vb'),
            'left': DeviceDataset('s1hl'),
            'right': DeviceDataset('s1hr'),
            'y_gap': DeviceDataset('s1v'),
            'x_gap': DeviceDataset('s1h'),
        },
        'slits_s2:NXslit': {
            'top': DeviceDataset('s2vt'),
            'bottom': DeviceDataset('s2vb'),
            'left': DeviceDataset('s2hl'),
            'right': DeviceDataset('s2hr'),
            'y_gap': DeviceDataset('s2v'),
            'x_gap': DeviceDataset('s2h'),
        },
        'slits_nose:NXslit': {
            'horizontal_position': DeviceDataset('snhm'),
            'vertical_position': DeviceDataset('snvm'),
        },
        'area_detector2:NXdetector': {
            'name': ConstDataset('EMBL-PSD', 'string'),
            'distance': DeviceDataset('detdist'),
            'polar_angle': DeviceDataset('stt', dtype='float32'),
            'tilt_angle': DeviceDataset('nu', dtype='float32'),
            'twotheta': DeviceDataset('stt', dtype='float32'),
            'x_pixel_offset': ConstDataset(128, 'float'),
            'y_pixel_offset': ConstDataset(64, 'float'),
            'x_pixel_size': ConstDataset(0.734, 'float',
                                         units=NXAttribute('mm', 'string')),
            'y_pixel_size': ConstDataset(1.4809, 'float',
                                         units=NXAttribute('mm', 'string')),
            'data': ImageDataset(0, 0, signal=NXAttribute(1, 'int32')),
            'x': FixedArray(-95, 0.734, 256),
            'y': FixedArray(-95, 1.4809, 128),
        },
    }

    _zebrablocklist = ['stt', 'om', 'chi', 'phi', 'nu', 'sgl', 'sgu']

    _zebra_sample = {
        'UB': ArrayParam('Sample', 'ubmatrix', 'float32'),
        'cell': CellArray(),
        'chi': DeviceDataset('chi', dtype='float32'),
        'phi': DeviceDataset('phi', dtype='float32'),
        'rotation_angle': DeviceDataset('om', dtype='float32'),
        'h': DeviceDataset('h'),
        'k': DeviceDataset('k'),
        'l': DeviceDataset('l'),
        'name': DeviceDataset('Sample', 'samplename'),
        'lieselotte': SaveSampleEnv(blocklist=_zebrablocklist),
    }

    def getTemplate(self):
        zebra_template = copy.deepcopy(self._zebra_default)
        zebra_template['entry1:NXentry']['ZEBRA:NXinstrument'] = \
            copy.deepcopy(self._zebra_instrument)
        if isinstance(session.instrument, EulerSXTal)\
                and session.instrument.use_psi:
            self._zebra_sample['psi'] = DeviceDataset('psi')
        zebra_template['entry1:NXentry']['sample:NXsample'] = \
            copy.deepcopy(self._zebra_sample)
        return zebra_template
