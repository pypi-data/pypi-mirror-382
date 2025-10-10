# -*- coding: UTF-8 -*-
"""
:filename: audioopy.audioutils.py
:author: Brigitte Bigi
:contributor: Nicolas Chazeau
:contact: contact@sppas.org
:summary: Utilities for manipulating audio.

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

from .aio import open as audio_open
from .aio import save as audio_save

from .audio import AudioPCM
from .channel import Channel
from .channelframes import ChannelFrames
from .channelformatter import ChannelFormatter

# ------------------------------------------------------------------------


def frames2times(frames, framerate):
    """Convert a list of frames into a list of time values.

    :param frames: (list) tuples (from_pos,to_pos)
    :param framerate: (int)
    :return: a list of tuples (from_time,to_time)

    """
    list_times = []
    fm = float(framerate)

    for (s, e) in frames:
        fs = float(s) / fm
        fe = float(e) / fm
        list_times.append((fs, fe))

    return list_times

# ------------------------------------------------------------------


def times2frames(times, framerate):
    """Convert a list of time' into a list of frame' values.

    :param times: (list)
    :param framerate: (int)
    :return: a list of tuples (from_pos,to_pos)

    """
    list_frames = []
    fm = float(framerate)
    for (s, e) in times:
        fs = int(s*fm)
        fe = int(e*fm)
        list_frames.append((fs, fe))

    return list_frames

# ------------------------------------------------------------------


def extract_audio_channel(input_audio, idx):
    """Return the channel of a specific index from an audio file name.

    :param input_audio: (str) Audio file name.
    :param idx: (int) Channel index

    """
    idx = int(idx)
    audio = audio_open(input_audio)
    i = audio.extract_channel(idx)
    channel = audio.get_channel(i)
    audio.close()

    return channel

# ------------------------------------------------------------------------


def extract_channel_fragment(channel, fromtime, totime, silence=0.):
    """Extract a fragment of a channel in the interval [fromtime,totime].
    Eventually, surround it by silences.

    :param channel:  (Channel)
    :param fromtime: (float) From time value in seconds.
    :param totime:   (float) To time value in seconds.
    :param silence:  (float) Duration value in seconds.

    """
    framerate = channel.get_framerate()

    # Extract the fragment of the channel
    startframe = int(fromtime*framerate)
    toframe = int(totime*framerate)
    fragmentchannel = channel.extract_fragment(begin=startframe, end=toframe)

    # Get all the frames of this fragment
    nbframes = fragmentchannel.get_nframes()
    cf = ChannelFrames(fragmentchannel.get_frames(nbframes))

    # surround by silences
    if silence > 0.:
        cf.prepend_silence(silence*framerate)
        cf.append_silence(silence*framerate)

    return Channel(16000, 2, cf.get_frames())

# ------------------------------------------------------------------------


def format_channel(channel, framerate, sampwidth):
    """Return a channel with the requested framerate and sampwidth.

    :param channel: (Channel)
    :param framerate: (int)
    :param sampwidth: (int) Either 1, 2 or 4

    """
    fm = channel.get_framerate()
    sp = channel.get_sampwidth()
    if fm != framerate or sp != sampwidth:
        formatter = ChannelFormatter(channel)
        formatter.set_framerate(framerate)
        formatter.set_sampwidth(sampwidth)
        formatter.convert()
        return formatter.get_channel()

    return channel

# ------------------------------------------------------------------------


def write_channel(audioname, channel):
    """Write a channel as an audio file.

    :param audioname: (str) Audio file name to write
    :param channel: (Channel) Channel to be saved

    """
    audio_out = AudioPCM()
    audio_out.append_channel(channel)
    audio_save(audioname, audio_out)
