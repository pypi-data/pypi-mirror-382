# -*- coding: UTF-8 -*-
"""
:filename: audioopy.audiovolume.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Estimate and store the RMS values of an audio.

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

from .audioframes import AudioFrames
from .basevolume import BaseVolume

# ----------------------------------------------------------------------------


class AudioVolume(BaseVolume):
    """Estimate the volume of an audio file.

    The volume is the estimation of RMS values, sampled with a default
    window of 10ms.

    """

    def __init__(self, audio, win_len=0.01):
        """Create an AudioVolume instance.

        :param audio: (AudioPCM) The audio to work on.
        :param win_len: (float) Window length to estimate the volume.

        """
        super(AudioVolume, self).__init__(win_len)

        # Remember current position
        pos = audio.tell()
        # Rewind to the beginning
        audio.rewind()

        # Find all the rms values
        nb_frames = int(win_len * audio.get_framerate())
        nb_vols = int(audio.get_duration()/win_len) + 1
        self._volumes = [0.] * nb_vols
        i = 0
        while audio.tell() < audio.get_nframes():
            frames = audio.read_frames(nb_frames)
            a = AudioFrames(frames, audio.get_sampwidth(), audio.get_nchannels())
            self._volumes[i] = a.rms()
            i += 1

        # Come back to the initial position
        audio.seek(pos)
        self._rms = audio.rms()
