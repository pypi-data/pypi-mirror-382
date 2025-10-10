"""
:filename: audioopy.channelformatter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tools to apply on frames of a channel.

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

from .channelframes import ChannelFrames
from .channel import Channel
from .audioframes import AudioFrames

# ---------------------------------------------------------------------------


class ChannelFormatter(object):
    """Utility to format frames of a channel.

    """
    def __init__(self, channel: Channel):
        """Create a ChannelFormatter instance.

        :param channel: (Channel) The channel to work on.
        :raises: TypeError: if channel is not a Channel instance.

        """
        if isinstance(channel, Channel) is False:
            raise TypeError(f"Given 'channel' must be of type Channel. "
                            f"Got {type(channel)} instead.")
        self._channel = channel
        self._framerate = channel.get_framerate()
        self._sampwidth = channel.get_sampwidth()

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_channel(self) -> Channel:
        """Return the Channel."""
        return self._channel

    # -----------------------------------------------------------------------

    def get_framerate(self) -> int:
        """Return the expected frame rate for the channel.

        Notice that while convert is not applied, it can be different of the
        current one of the channel.

        :return: (int) the frame rate that will be used by the converter

        """
        return self._framerate

    # -----------------------------------------------------------------------

    def get_sampwidth(self) -> int:
        """Return the expected sample width for the channel.

        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        :return: (int) the sample width that will be used by the converter

        """
        return self._sampwidth

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_framerate(self, framerate: int):
        """Fix the expected frame rate for the channel.

        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        :param framerate: (int) Commonly 8000, 16000 or 48000

        """
        self._framerate = int(framerate)

    # -----------------------------------------------------------------------

    def set_sampwidth(self, sampwidth: int):
        """Fix the expected sample width for the channel.

        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        :param sampwidth: (int) 1, 2 or 4

        """
        self._sampwidth = int(sampwidth)

    # -----------------------------------------------------------------------

    def convert(self):
        """Convert the channel.

        Convert to the expected (already) given sample width and frame rate.

        """
        new_channel = Channel()
        new_channel.set_frames(self.__convert_frames(self._channel.get_frames()))
        new_channel.set_sampwidth(self._sampwidth)
        new_channel.set_framerate(self._framerate)

        self._channel = new_channel

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def bias(self, bias_value: int):
        """Convert the channel with a bias added to each frame.

        Samples wrap around in case of overflow.

        :param bias_value: (int) the value to bias the frames

        """
        bias_value = int(bias_value)
        if bias_value == 0:
            return
        current_frames = self._channel.get_frames()
        a = AudioFrames(current_frames, self._channel.get_sampwidth(), 1)
        self._channel.set_frames(a.bias(bias_value))

    # -----------------------------------------------------------------------

    def mul(self, factor: float):
        """Convert the channel.

        All frames in the original channel are multiplied by the floating-point
        value factor.
        Samples are truncated in case of overflow.

        :param factor: (float) the factor to multiply the frames

        """
        factor = float(factor)
        if factor == 1.:
            return

        current_frames = self._channel.get_frames()
        a = AudioFrames(current_frames, self._channel.get_sampwidth(), 1)
        self._channel.set_frames(a.mul(factor))

    # ----------------------------------------------------------------------

    def remove_offset(self):
        """Convert the channel by removing the offset in the channel.

        """
        current_frames = self._channel.get_frames()
        a = AudioFrames(current_frames, self._channel.get_sampwidth(), 1)
        avg = round(a.avg(), 0)
        self._channel.set_frames(a.bias(- avg))

    # ----------------------------------------------------------------------

    def sync(self, channel: Channel):
        """Convert the channel with the parameters from the channel put in input.

        :param channel: (Channel) the channel used as a model

        """
        if isinstance(channel, Channel) is not True:
            raise TypeError("Expected a channel, got %s" % type(channel))

        self._sampwidth = channel.get_sampwidth()
        self._framerate = channel.get_framerate()
        self.convert()

    # ----------------------------------------------------------------------

    def remove_frames(self, begin: int, end: int):
        """Convert the channel by removing frames.

        :param begin: (int) the position of the beginning of the frames to remove (included)
        :param end: (int) the position of the end of the frames to remove (included)
        :raises: ValueError: invalid begin or end

        """
        begin = int(begin)
        end = int(end)
        if begin > end:
            raise ValueError("The 'end' index must be greater than 'begin'.")
        if begin < 0 or end+1 < 0:
            raise ValueError("Indices 'begin' and 'end' must be non-negative.")

        frame_length = len(self._channel.get_frames()) // self._sampwidth
        if end+1 > frame_length:
            raise ValueError(f"'end' index {end} exceeds the number of frames {frame_length}.")

        # Compute byte positions
        byte_begin = begin * self._sampwidth
        byte_end = (end+1) * self._sampwidth

        # Update frames
        current_frames = self._channel.get_frames()
        updated_frames = current_frames[:byte_begin] + current_frames[byte_end:]

        self._channel.set_frames(updated_frames)

    # ----------------------------------------------------------------------

    def add_frames(self, frames: bytes, position: int):
        """Convert the channel by adding frames.

        :param frames: (bytes) Audio frames
        :param position: (int) the position where the frames will be inserted
        :raises: ValueError: invalid frames

        """
        position = int(position)
        if isinstance(frames, bytes) is False:
            raise TypeError("'frames' must be of type bytes.")
        if len(frames) % self._sampwidth != 0:
            raise ValueError(f"Length of 'frames' ({len(frames)}) must be a multiple of sampwidth ({self._sampwidth}).")
        if position < 0:
            raise ValueError("Position must be non-negative.")

        frame_length = len(self._channel.get_frames()) // self._sampwidth
        if position > frame_length:
            raise ValueError(f"Position {position} exceeds the number of frames {frame_length}.")

        # Compute byte position
        byte_position = position * self._sampwidth

        # Update frames: Inserting frames at the given position
        current_frames = self._channel.get_frames()
        updated_frames = current_frames[:byte_position] + frames + current_frames[byte_position:]

        self._channel.set_frames(updated_frames)

    # ----------------------------------------------------------------------

    def append_frames(self, frames: bytes):
        """Convert the channel by appending frames.

        :param frames: (bytes) the frames to append

        """
        if isinstance(frames, bytes) is False:
            raise TypeError("'frames' must be of type bytes.")
        if len(frames) % self._sampwidth != 0:
            raise ValueError(f"Length of 'frames' ({len(frames)}) must be a multiple of sampwidth ({self._sampwidth}).")
        if len(frames) == 0:
            return
        current_frames = self._channel.get_frames()
        updated_frames = current_frames + frames
        self._channel.set_frames(updated_frames)

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def __convert_frames(self, frames: str):
        """Convert frames to the expected sample width and frame rate.

        :param frames: (str) the frames to convert

        """
        f = frames
        fragment = ChannelFrames(f)

        # Convert the sample width if it needs to
        if self._channel.get_sampwidth() != self._sampwidth:
            fragment.change_sampwidth(self._channel.get_sampwidth(), self._sampwidth)

        # Convert the self._framerate if it needs to
        if self._channel.get_framerate() != self._framerate:
            fragment.resample(self._sampwidth, self._channel.get_framerate(), self._framerate)

        return fragment.get_frames()
