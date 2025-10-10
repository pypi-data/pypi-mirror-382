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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
import json
import time

import numpy as np
from streaming_data_types import deserialise_hs00, deserialise_hs01
from streaming_data_types.utils import get_schema

from nicos.core import ArrayDesc, InvalidValueError, Override, Param, Value, \
    floatrange, listof, multiStatus, oneof, status, tupleof
from nicos.core.constants import LIVE, MASTER, SIMULATION
from nicos.core.device import DeviceMetaInfo, DeviceParInfo
from nicos.devices.generic import Detector, ImageChannelMixin, PassiveChannel
from nicos.utils import createThread

from nicos_ess.devices.kafka.consumer import KafkaConsumer, KafkaSubscriber
from nicos_ess.devices.kafka.producer import KafkaProducer
from nicos_ess.devices.kafka.status_handler import DISCONNECTED_STATE, \
    KafkaStatusHandler


class Hist1dTof:
    name = 'hist1d'

    @classmethod
    def get_array_description(cls, name, num_bins, **ignored):
        return ArrayDesc(name, shape=(num_bins, ), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, num_bins, **ignored):
        return cls.transform_data(
            np.zeros(shape=(num_bins, ), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        return data

    @classmethod
    def get_info(cls, name, num_bins, **ignored):
        return [
            DeviceMetaInfo(
                f'{name} bins',
                DeviceParInfo(num_bins, str(num_bins), '', 'general'))]


class Hist2dTof:
    name = 'hist2d'

    @classmethod
    def get_array_description(cls, name, num_bins, **ignored):
        return ArrayDesc(name, shape=(num_bins, num_bins), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, num_bins, **ignored):
        return cls.transform_data(
            np.zeros(shape=(num_bins, num_bins), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, num_bins, **ignored):
        return [DeviceMetaInfo(
            f'{name} bins', DeviceParInfo(
                (num_bins, num_bins), str((num_bins, num_bins)), '',
                'general'))]


class Hist2dDet:
    name = 'dethist'

    @classmethod
    def get_array_description(cls, name, det_width, det_height, **ignored):
        return ArrayDesc(name, shape=(det_width, det_height), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, det_width, det_height, **ignored):
        return cls.transform_data(
            np.zeros(shape=(det_width, det_height), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, det_width, det_height, **ignored):
        return [
            DeviceMetaInfo(
                f'{name} width', DeviceParInfo(det_width, str(det_width),
                                               '', 'general')),
            DeviceMetaInfo(
                f'{name} height', DeviceParInfo(det_height, str(det_height),
                                                '', 'general'))]


class Hist2dRoi:
    name = 'roihist'

    @classmethod
    def get_array_description(cls, name, det_width, left_edges, **ignored):
        return ArrayDesc(name, shape=(det_width, left_edges), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, det_width, left_edges, **ignored):
        return cls.transform_data(
            np.zeros(shape=(det_width, left_edges), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, det_width, left_edges, **ignored):
        height = len(left_edges)
        return [
            DeviceMetaInfo(
                f'{name} width', DeviceParInfo(det_width, str(det_width), '',
                                               'general')),
            DeviceMetaInfo(
                f'{name} height', DeviceParInfo(height, str(height), '',
                                                'general'))]


hist_type_by_name = {
    '1-D TOF': Hist1dTof,
    '2-D TOF': Hist2dTof,
    '2-D DET': Hist2dDet,
    '2-D ROI': Hist2dRoi,
}

deserialiser_by_schema = {
    'hs00': deserialise_hs00,
    'hs01': deserialise_hs01,
}


class JustBinItImage(KafkaSubscriber, ImageChannelMixin, PassiveChannel):
    parameters = {
        'hist_topic':
            Param(
                'The topic to listen on for the histogram data',
                type=str,
                userparam=False,
                settable=False,
                mandatory=True,
            ),
        'data_topic':
            Param(
                'The topic to listen on for the event data',
                type=str,
                userparam=False,
                settable=False,
                mandatory=True,
            ),
        'hist_type':
            Param('The number of dimensions to histogram in',
                  type=oneof(*hist_type_by_name.keys()),
                  default='1-D TOF',
                  userparam=True,
                  settable=True),
        'tof_range':
            Param(
                'The time-of-flight range to histogram',
                type=tupleof(int, int),
                default=(0, 100000000),
                userparam=True,
                settable=True,
            ),
        'det_range':
            Param(
                'The detector range to histogram over',
                type=tupleof(int, int),
                default=(0, 100),
                userparam=True,
                settable=True,
            ),
        'det_width':
            Param('The width in pixels of the detector',
                  type=int,
                  default=10,
                  userparam=True,
                  settable=True),
        'det_height':
            Param('The height in pixels of the detector',
                  type=int,
                  default=10,
                  userparam=True,
                  settable=True),
        'num_bins':
            Param(
                'The number of bins to histogram into',
                type=int,
                default=50,
                userparam=True,
                settable=True,
            ),
        'left_edges':
            Param(
                'The left edges for a ROI histogram',
                type=listof(int),
                default=[],
                userparam=True,
                settable=True,
            ),
        'source':
            Param(
                'Identifier source on multiplexed topics',
                type=str,
                default='',
                userparam=True,
                settable=True,
            ),
        'rotation':
            Param(
                'Rotation angle to apply to the image',
                type=oneof(0, 90, 180, 270),
                default=90,
                userparam=True,
                settable=True,
            ),
    }

    parameter_overrides = {
        'unit':
            Override(default='events', settable=False, mandatory=False),
        'fmtstr':
            Override(default='%d'),
        'pollinterval':
            Override(default=None, userparam=False, settable=False),
    }

    def doPreinit(self, mode):
        self._unique_id = None
        self._current_status = (status.OK, '')
        if mode == SIMULATION:
            return
        self._update_status(status.OK, '')
        # Set up the data consumer
        KafkaSubscriber.doPreinit(self, None)

    def doInit(self, mode):
        self._hist_sum = 0
        self._zero_data()

    def _zero_data(self):
        self._hist_data = hist_type_by_name[self.hist_type].get_zeroes(
            **self._params)

    def arrayInfo(self):
        return hist_type_by_name[self.hist_type].get_array_description(
            **self._params)

    def doPrepare(self):
        self._update_status(status.BUSY, 'Preparing')
        self._zero_data()
        self._hist_edges = np.array([])
        self._hist_sum = 0
        try:
            self.subscribe(self.hist_topic)
        except Exception as error:
            self._update_status(status.ERROR, str(error))
            raise
        self._update_status(status.OK, '')

    def new_messages_callback(self, messages):
        for _, message in messages:
            deserialiser = deserialiser_by_schema.get(get_schema(message))
            if not deserialiser:
                continue
            hist = deserialiser(message)
            info = json.loads(hist['info'])
            self.log.debug('received unique id = %s', info['id'])
            if info['id'] != self._unique_id:
                continue
            if info['state'] in ['COUNTING', 'INITIALISED']:
                self._update_status(status.BUSY, 'Counting')
            elif info['state'] == 'ERROR':
                error_msg = info[
                    'error_message'] if 'error_message' in info else 'unknown error'
                self._update_status(status.ERROR, error_msg)
            elif info['state'] == 'FINISHED':
                self._halt_consumer_thread()
                self._consumer.unsubscribe()
                self._update_status(status.OK, '')
                break

            self._hist_data = hist_type_by_name[self.hist_type].transform_data(
                hist['data'], rotation=self.rotation)
            self._hist_sum = self._hist_data.sum()
            self._hist_edges = hist['dim_metadata'][0]['bin_boundaries']

    def _update_status(self, new_status, message):
        self._current_status = new_status, message
        self._cache.put(self._name, 'status', self._current_status,
                        time.time())

    def doRead(self, maxage=0):
        return [self._hist_sum]

    def doReadArray(self, quality):
        return self._hist_data

    def valueInfo(self):
        return (Value(self.name, fmtstr='%d'), )

    def doStart(self):
        self._update_status(status.BUSY, 'Waiting to start...')

    def doStop(self):
        self._update_status(status.OK, '')

    def doStatus(self, maxage=0):
        return self._current_status

    def _halt_consumer_thread(self, join=False):
        if self._updater_thread is not None:
            self._stoprequest = True
            if join and self._updater_thread.is_alive():
                self._updater_thread.join()

    def get_configuration(self):
        # Generate a unique-ish id
        self._unique_id = 'nicos-{}-{}'.format(self.name, int(time.time()))

        return {
            'type': hist_type_by_name[self.hist_type].name,
            'data_brokers': self.brokers,
            'data_topics': [self.data_topic],
            'tof_range': list(self.tof_range),
            'det_range': list(self.det_range),
            'num_bins': self.num_bins,
            'width': self.det_width,
            'height': self.det_height,
            'left_edges': self.left_edges,
            'topic': self.hist_topic,
            'source': self.source,
            'id': self._unique_id,
        }

    def doInfo(self):
        result = [
            DeviceMetaInfo(
                f'{self.name} histogram type',
                DeviceParInfo(self.hist_type, self.hist_type, '', 'general'))]
        result.extend(
            hist_type_by_name[self.hist_type].get_info(**self._params))
        return result


class JustBinItDetector(Detector, KafkaStatusHandler):
    """ A "detector" that reads image data from just-bin-it.

    Note: it only uses image channels.
    """
    parameters = {
        'command_topic':
            Param(
                'The topic to send just-bin-it commands to',
                type=str,
                userparam=False,
                settable=False,
                mandatory=True,
            ),
        'response_topic':
            Param(
                'The topic where just-bin-it responses appear',
                type=str,
                userparam=False,
                settable=False,
                mandatory=True,
            ),
        'ack_timeout':
            Param(
                'How long to wait for timeout on acknowledgement',
                type=int,
                default=5,
                unit='s',
                userparam=False,
                settable=False,
            ),
        'hist_schema':
            Param(
                'Which schema to use for histograms',
                type=oneof(*deserialiser_by_schema.keys()),
                default='hs00',
                userparam=False,
                settable=True,
            ),
        'event_schema':
            Param(
                'Which schema the event data uses',
                type=oneof('ev42', 'ev44'),
                default='ev42',
                userparam=False,
                settable=True,
            ),
    }

    parameter_overrides = {
        'unit':
            Override(default='events', settable=False, mandatory=False),
        'fmtstr':
            Override(default='%d'),
        'liveinterval':
            Override(type=floatrange(0.5), default=1),
        'pollinterval':
            Override(default=None, userparam=False, settable=False),
        'statustopic':
            Override(default='', mandatory=False),
    }
    _last_live = 0
    _presetkeys = {'t'}
    _ack_thread = None
    _conditions_thread = None
    _exit_thread = False
    _conditions = {}
    hardware_access = True

    def doPreinit(self, mode):
        presetkeys = {'t'}
        for image_channel in self._attached_images:
            presetkeys.add(image_channel.name)
        self._presetkeys = presetkeys
        if mode == SIMULATION:
            return

        if self.statustopic:
            # Enable heartbeat monitoring
            KafkaStatusHandler.doPreinit(self, mode)
        self._command_sender = KafkaProducer.create(self.brokers)
        # Set up the response message consumer
        self._response_consumer = KafkaConsumer.create(self.brokers)
        self._response_consumer.subscribe(self.response_topic)

    def doInit(self, mode):
        pass

    def doPrepare(self):
        self._exit_thread = False
        self._conditions_thread = None
        for image_channel in self._attached_images:
            image_channel.doPrepare()

    def doStart(self, **preset):
        self._last_live = -(self.liveinterval or 0)

        # Generate a unique-ish id
        unique_id = 'nicos-{}-{}'.format(self.name, int(time.time()))
        self.log.debug('set unique id = %s', unique_id)

        self._conditions = {}

        for image_channel in self._attached_images:
            val = self._lastpreset.get(image_channel.name, 0)
            if val:
                self._conditions[image_channel] = val

        count_interval = self._lastpreset.get('t', None)
        config = self._create_config(count_interval, unique_id)

        if count_interval:
            self.log.debug(
                'Requesting just-bin-it to start counting for %s seconds',
                count_interval)
        else:
            self.log.debug('Requesting just-bin-it to start counting')

        self._send_command(self.command_topic, json.dumps(config).encode())

        # Tell the channels to start
        for image_channel in self._attached_images:
            image_channel.doStart()

        # Check for acknowledgement of the command being received
        self._ack_thread = createThread('jbi-ack', self._check_for_ack,
                                        (unique_id, self.ack_timeout))

    def _check_for_ack(self, identifier, timeout_duration):
        timeout = int(time.time()) + timeout_duration
        acknowledged = False
        while not (acknowledged or self._exit_thread):
            message = self._response_consumer.poll(timeout_ms=50)
            if message:
                msg = json.loads(message.value())
                if 'msg_id' in msg and msg['msg_id'] == identifier:
                    acknowledged = self._handle_message(msg)
                    break
            # Check for timeout
            if not acknowledged and int(time.time()) > timeout:
                err_msg = 'Count aborted as no acknowledgement received from ' \
                          'just-bin-it within timeout duration '\
                          f'({timeout_duration} seconds)'
                self.log.error(err_msg)
                break
        if not acknowledged:
            # Couldn't start histogramming, so stop the channels etc.
            self._stop_histogramming()
            for image_channel in self._attached_images:
                image_channel.doStop()
            return

        if self._conditions:
            self._conditions_thread = createThread('jbi-conditions',
                                                   self._check_conditions,
                                                   (self._conditions.copy(), ))

    def _check_conditions(self, conditions):
        while not self._exit_thread:
            if conditions and all(ch.read()[0] >= val
                                  for ch, val in conditions.items()):
                self._stop_histogramming()
                break
            time.sleep(0.1)

    def _handle_message(self, msg):
        if 'response' in msg and msg['response'] == 'ACK':
            self.log.debug('Counting request acknowledged by just-bin-it')
            return True
        elif 'response' in msg and msg['response'] == 'ERR':
            self.log.error('just-bin-it could not start counting: %s',
                           msg['message'])
        else:
            self.log.error(
                'Unknown response message received from just-bin-it')
        return False

    def _send_command(self, topic, message):
        self._command_sender.produce(topic, message)

    def _create_config(self, interval, identifier):
        histograms = []

        for image_channel in self._attached_images:
            histograms.append(image_channel.get_configuration())

        config_base = {
            'cmd': 'config',
            'msg_id': identifier,
            'input_schema': self.event_schema,
            'output_schema': self.hist_schema,
            'histograms': histograms
        }

        if interval:
            config_base['interval'] = interval
        else:
            # If no interval then start open-ended count
            config_base['start'] = int(time.time()) * 1000
        return config_base

    def valueInfo(self):
        return tuple(info for channel in self._attached_images
                     for info in channel.valueInfo())

    def doRead(self, maxage=0):
        return [
            data for channel in self._attached_images
            for data in channel.read(maxage)
        ]

    def doReadArrays(self, quality):
        return [image.readArray(quality) for image in self._attached_images]

    def _stop_histogramming(self):
        self._send_command(self.command_topic, b'{"cmd": "stop"}')

    def doShutdown(self):
        self._response_consumer.close()

    def doSetPreset(self, **preset):
        if not preset:
            # keep old settings
            return
        for i in preset:
            if i not in self._presetkeys:
                valid_keys = ', '.join(self._presetkeys)
                raise InvalidValueError(
                    self, f'unrecognised preset {i}, should'
                    f' one of {valid_keys}')
        if 't' in preset and \
                len(self._presetkeys.intersection(preset.keys())) > 1:
            raise InvalidValueError(
                self, 'Cannot set number of detector counts'
                ' and a time interval together')
        self._lastpreset = preset.copy()

    def doStop(self):
        self._do_stop()

    def doFinish(self):
        self._do_stop()

    def _do_stop(self):
        self._stop_job_threads()
        self._stop_histogramming()

    def _stop_job_threads(self):
        self._exit_thread = True
        self._stop_thread(self._ack_thread)
        self._stop_thread(self._conditions_thread)

    def _stop_thread(self, thread):
        if thread and thread.is_alive():
            thread.join()

    def doStatus(self, maxage=0):
        curstatus = self._cache.get(self, 'status')
        if curstatus and curstatus[0] == status.ERROR:
            return curstatus
        return multiStatus(self._attached_images, maxage)

    def _status_update_callback(self, messages):
        # Called on heartbeat received
        if self._mode == MASTER:
            if self._cache.get(self, 'status') == DISCONNECTED_STATE:
                self._cache.put(self, 'status', (status.OK, ''), time.time())

    def no_messages_callback(self):
        if self._mode == MASTER and not self.is_process_running():
            # No heartbeat
            self._cache.put(self, 'status', DISCONNECTED_STATE, time.time())

    def doReset(self):
        pass

    def doInfo(self):
        return [
            data for channel in self._attached_images
            for data in channel.doInfo()
        ]

    def duringMeasureHook(self, elapsed):
        if self.liveinterval is not None:
            if elapsed > self._last_live + self.liveinterval:
                self._last_live = elapsed
                return LIVE
        return None

    def arrayInfo(self):
        return tuple(image.arrayInfo() for image in self._attached_images)

    def doTime(self, preset):
        return 0

    def presetInfo(self):
        return tuple(self._presetkeys)
