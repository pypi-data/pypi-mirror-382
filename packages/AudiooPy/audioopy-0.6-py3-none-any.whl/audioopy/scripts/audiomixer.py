#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: audioopy.scripts.audioformat.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A script to mix all channels of audio files.

.. _This file is part of AudiooPy:
..
    ---------------------------------------------------------------------

    Copyright (C) 2024-2025  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    AudiooPy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    AudiooPy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with AudiooPy. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    ---------------------------------------------------------------------

"""

from argparse import ArgumentParser
import os
import sys

PROGRAM = os.path.abspath(__file__)
AUDIOOPY = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.insert(0, AUDIOOPY)

import audioopy.aio
from audioopy import ChannelMixer
from audioopy import ChannelFormatter
from audioopy import ChannelFrames
from audioopy import AudioPCM

# ----------------------------------------------------------------------------


def get_args_from_cmd():

    parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM),
                            description="... a script to mix all channels of one or several audio files.")

    parser.add_argument("-w",
                        metavar="file",
                        action='append',
                        required=True,
                        help='Input audio filename (append mode)')

    parser.add_argument("-r",
                        metavar="rate",
                        required=False,
                        default=16000,
                        type=int,
                        help='Output audio framerate. (default: 16000)')

    parser.add_argument("-o",
                        metavar="file",
                        required=True,
                        help='Output audio filename')

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    return parser.parse_args()

# ----------------------------------------------------------------------------


def audiomixer():
    args = get_args_from_cmd()
    framerate = args.r
    sampwidth = 2

    mixer = ChannelMixer()
    audios = list()
    max_duration = 0
    for input_file in args.w:
        audio = audioopy.aio.open(input_file)
        audios.append(audio)
        if audio.get_duration() > max_duration:
            max_duration = audio.get_duration()

    for audio in audios:
        for i in range(audio.get_nchannels()):
            idx = audio.extract_channel(i)
            audio.rewind()

            # Mixed channels must have the same framerate and sample width.
            formatter = ChannelFormatter(audio.get_channel(idx))
            formatter.set_framerate(framerate)
            formatter.set_sampwidth(sampwidth)
            formatter.convert()

            # Append silence to ensure having the same duration for all channels
            if audio.get_duration() < max_duration:
                delta_duration = max_duration - audio.get_duration()
                silent_frames = ChannelFrames()
                silent_frames.prepend_silence(delta_duration * framerate)
                formatter.append_frames(silent_frames.get_frames())

            mixer.append_channel(formatter.get_channel())
        audio.close()

    new_channel = mixer.mix()

    # Save the converted channel
    audio_out = AudioPCM()
    audio_out.append_channel(new_channel)
    audioopy.aio.save(args.o, audio_out)

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    audiomixer()
