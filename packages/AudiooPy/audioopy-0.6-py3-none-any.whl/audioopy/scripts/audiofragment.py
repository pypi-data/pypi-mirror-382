#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: audioopy.scripts.audiofragment.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Extract a fragment of an audio file.

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
from audioopy.audio import AudioPCM

# ----------------------------------------------------------------------------


def get_args_from_cmd():
    """Get args from the command-line interface with ArgumentParser."""

    parser = ArgumentParser(usage="%s -w input file -o output file [OPTIONS]" % os.path.basename(PROGRAM),
                            description="... a script to extract a fragment of an audio file.")

    parser.add_argument("-w",
                        metavar="file",
                        required=True,
                        help='Input audio filename')

    parser.add_argument("-o",
                        metavar="file",
                        required=True,
                        help='Output audio filename')

    begin_group = parser.add_mutually_exclusive_group()
    begin_group.add_argument("-bs", default=0., metavar="value", type=float,
                             help='The position (in seconds) when begins the mix (default: 0.).')

    begin_group.add_argument("-bf", default=0, metavar="value", type=int,
                             help='The position (in number of frames) when begins the mix (default: 0).')

    end_group = parser.add_mutually_exclusive_group()
    end_group.add_argument("-es", default=0., metavar="value", type=float,
                           help='The position (in seconds) when ends the mix (default: audio length).')

    end_group.add_argument("-ef", default=0, metavar="value", type=int,
                           help='The position (in number of frames) when ends the mix (default: audio length).')

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    return parser.parse_args()

# ----------------------------------------------------------------------------


def audiofragment():

    args = get_args_from_cmd()

    audio_out = AudioPCM()
    audio = audioopy.aio.open(args.w)

    if args.bf:
        begin = args.bf
    elif args.bs:
        begin = int(args.bs * float(audio.get_framerate()))
    else:
        begin = 0

    if args.ef:
        end = args.ef
    elif args.es:
        end = int(args.es * float(audio.get_framerate()))
    else:
        end = audio.get_nframes()

    print(begin)
    print(end)

    for i in range(audio.get_nchannels()):
        idx = audio.extract_channel(i)
        audio.rewind()
        channel = audio.get_channel(idx)
        extracter = channel.extract_fragment(begin, end)
        audio_out.append_channel(extracter)

    audioopy.aio.save(args.o, audio_out)

# ----------------------------------------------------------------------------


if __name__ == "__main__":
    audiofragment()
