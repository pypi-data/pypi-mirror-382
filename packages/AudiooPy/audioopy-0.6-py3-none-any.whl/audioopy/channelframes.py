"""
:filename: audioopy.channelframes.py
:author: Brigitte Bigi
:contributor: Nicolas Chazeau
:contact: contact@sppas.org
:summary: Represent frames of a channel.

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

# ---------------------------------------------------------------------------


class ChannelFrames(object):
    """Data structure to deal with the frames of a channel.

    """
    def __init__(self, frames=b""):
        """Create a ChannelFrames instance.

        :param frames: (str) Frames that must be MONO ONLY.

        """
        self._frames = frames

    # -----------------------------------------------------------------------

    def get_frames(self):
        """Return the frames

        :return: (str) the frames

        """
        return self._frames

    # ----------------------------------------------------------------------------

    def set_frames(self, frames):
        """Set the frames.

        :param frames: (str) the frames to set

        """
        self._frames = frames

    # ----------------------------------------------------------------------------

    def append_silence(self, nframes):
        """Create n frames of silence and append it to the frames.

        :param nframes: (int) the number of frames of silence to append

        """
        nframes = int(nframes)
        if nframes <= 0:
            return False

        self._frames += b" \x00" * nframes
        return True

    # ----------------------------------------------------------------------------

    def prepend_silence(self, nframes):
        """Create n frames of silence and prepend it to the frames.

        :param nframes: (int) the number of frames of silence to append

        """
        nframes = int(nframes)
        if nframes <= 0:
            return False

        self._frames = b" \x00" * nframes + self._frames
        return True

    # ----------------------------------------------------------------------------

    def resample(self, sampwidth, rate, newrate):
        """Resample the frames with a new frame rate.

        :param sampwidth: (int) sample width of the frames.
        :param rate: (int) current frame rate of the frames
        :param newrate: (int) new frame rate of the frames

        """
        if rate != newrate:
            a = AudioFrames(self._frames, sampwidth, 1)
            self._frames = a.resample(rate, newrate)

    # ----------------------------------------------------------------------------

    def change_sampwidth(self, sampwidth, newsampwidth):
        """Change the number of bytes used to encode the frames.

        :param sampwidth: (int) current sample width of the frames.
        (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        :param newsampwidth: (int) new sample width of the frames.
        (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)

        """
        if sampwidth != newsampwidth:
            a = AudioFrames(self._frames, sampwidth, 1)
            self._frames = a.change_sampwidth(newsampwidth)

    # ----------------------------------------------------------------------------

    @staticmethod
    def get_minval(size, signed=True):
        return AudioFrames().get_minval(size, signed)

    # ----------------------------------------------------------------------------

    @staticmethod
    def get_maxval(size, signed=True):
        return AudioFrames().get_maxval(size, signed)
