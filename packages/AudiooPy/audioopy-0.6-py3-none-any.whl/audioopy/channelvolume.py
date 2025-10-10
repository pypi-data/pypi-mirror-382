# -*- coding: UTF-8 -*-
"""
:filename: audioopy.channelvolume.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Estimate and store the RMS values of a channel.

.. _This file was initially part of SPPAS: <https://sppas.org>
.. _This file is now part of AudiooPy:
..
    ---------------------------------------------------------------------

    Copyright (C) 2024-2025  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Affero Public License, version 3.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    ---------------------------------------------------------------------

"""

from __future__ import annotations
import logging

from .channel import Channel
from .audioframes import AudioFrames
from .basevolume import BaseVolume

# ----------------------------------------------------------------------------


class ChannelVolume(BaseVolume):
    """Estimate stats of the volume of an audio channel.

    It extends the BaseVolume class to estimate and analyze the volume (rms)
    of an audio channel over specified time windows. It calculates rms values
    for segments of audio data and provides statistical measures for these
    values.

    Main functionalities:

    - Estimate rms values for segments of an audio channel.
    - Calculate statistical measures such as mean, median, variance, standard deviation, and z-scores for the calculated rms values.

    """

    def __init__(self, channel: Channel, win_len: float = 0.01):
        """Create a volume estimator for the given channel.

        Fields:

        - _channel: (Channel) The audio channel being analyzed.
        - _win_len: (float) The window length used for estimating rms values.
        - _volumes: (list) List of calculated rms values.
        - _rms: (float) The global rms value of the channel.

        :param channel: (Channel) The channel to work on.
        :param win_len: (float) Window length to estimate the volume.

        """
        super(ChannelVolume, self).__init__(win_len)

        # Remember current position
        pos = channel.tell()
        # Rewind to the beginning
        channel.rewind()

        self._channel = channel
        self._win_len = win_len
        self._volumes = ChannelVolume.calculate_volumes(channel, win_len)

        # Returns to the position where we were before
        channel.seek(pos)
        self._rms = channel.rms()

    # -----------------------------------------------------------------------

    def set_volume_value(self, index: int, value: float) -> None:
        """Set manually the rms at a given position.

        :param index: (int) The index of the value to set.
        :param value: (float) The value of the channel.

        """
        self._volumes[index] = value

    # -----------------------------------------------------------------------

    def evaluate(self, win_len: float = 0.01) -> None:
        """Force to re-estimate the global rms value and re-assign all members.

        :param win_len: (float) Window length to estimate the volume.

        """
        # Remember current position
        pos = self._channel.tell()
        # Rewind to the beginning
        self._channel.rewind()

        """
        nb_frames = int(win_len * self._channel.get_framerate())
        nb_vols = int(self._channel.get_duration()/win_len) + 1
        previous_rms = 0
        for i in range(nb_vols):
            frames = self._channel.get_frames(nb_frames)
            a = AudioFrames(frames, self._channel.get_sampwidth(), 1)
            rms = a.rms()
            if rms > 0:  # provide negative values of corrupted audio files
                self._volumes[i] = rms
            elif rms < 0:
                self._volumes[i] = previous_rms
                logging.warning("Corrupted audio? The RMS shouldn't be a negative value. Got {}.".format(rms))
            previous_rms = rms
        """
        volumes = ChannelVolume.calculate_volumes(self._channel, self._win_len)

        # Return at the position where we were before
        self._channel.seek(pos)

        # Assign all members
        self._volumes = volumes
        self._rms = self._channel.rms()
        self._win_len = win_len

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def calculate_volumes(channel: Channel, win_len: float = 0.01) -> list:
        """Estimate the volume values of an audio channel.

        Computes the Root Mean Square (RMS) values of audio frames in a given
        channel over specified time windows. It handles corrupted audio by
        logging warnings and using the previous RMS value for negative RMS
        readings.

        Flow:

        1. Calculate the number of frames per window and the total number of windows.
        2. Initialize a list to store RMS values and set the initial previous_rms to 0.
        3. Loop through each window, extract frames, and compute the RMS value.
        4. If the RMS value is positive, store it; if negative, log a warning and use the previous RMS value.
        5. Return the list of RMS values.

        :example:
        >>> channel = Channel(framerate=16000, sampwidth=2, frames=b'\x01\x00\x02\x00\x03\x00\x04\x00')
        >>> volumes = ChannelVolume.calculate_volumes(channel, win_len=0.01)
        >>> print(volumes)
        [2.74]

        :param channel: (Channel) The channel to work on.
        :param win_len: (float) Window length to estimate the volume.
        :return: (list) The volume values.

        """
        nb_frames = int(win_len * channel.get_framerate())
        nb_vols = int(channel.get_duration()/win_len) + 1
        volumes = [0.] * nb_vols
        previous_rms = 0

        for i in range(nb_vols):
            frames = channel.get_frames(nb_frames)
            a = AudioFrames(frames, channel.get_sampwidth(), 1)
            rms = a.rms()
            if rms > 0:  # provide negative values of corrupted audio files
                volumes[i] = rms
            elif rms < 0:
                volumes[i] = previous_rms
                logging.warning("Corrupted audio? The RMS shouldn't be a negative value but got {}"
                                "".format(rms))
            previous_rms = rms

        # remove last estimated value if un-significant
        if len(volumes) > 0 and volumes[-1] == 0:
            volumes.pop()

        return volumes

    # -----------------------------------------------------------------------

    def normalize_volumes(self) -> int:
        """Remove outliers from the volume statistics of the channel.

        It sorts the volume values, determines a threshold at the 85th percentile,
        and caps any volume values above this threshold to the threshold value.

        :return: (int) Number of modified outliers.

        """
        if len(self._volumes) == 0:
            return 0
        nb = 0
        sorted_volumes = sorted(self._volumes)
        rms_threshold = sorted_volumes[int(0.85 * len(sorted_volumes))]
        for i, v in enumerate(self._volumes):
            if v > rms_threshold:
                self._volumes[i] = rms_threshold
                nb += 1
        return nb

    # -----------------------------------------------------------------------

    def __repr__(self):
        return str(self._volumes)
