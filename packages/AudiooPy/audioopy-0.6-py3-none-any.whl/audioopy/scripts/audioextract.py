#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: audioopy.scripts.audioextract.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A script to extract a channel from an audio file.

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

from audioopy.audio import AudioPCM
from audioopy.aio import open as aio_open
from audioopy.aio import save as aio_save

# ----------------------------------------------------------------------------


def get_args_from_cmd():
    parser = ArgumentParser(usage="%s -w input file -o output file -c channel" % os.path.basename(PROGRAM),
                            description="... a script to extract a channel from an audio file.")

    parser.add_argument("-w",
                        metavar="file",
                        required=True,
                        help='Audio Input file name')

    parser.add_argument("-o",
                        metavar="file",
                        required=True,
                        help='Audio Output file name')

    parser.add_argument("-c",
                        metavar="value",
                        default=1,
                        type=int,
                        required=False,
                        help='Number of the channel to extract (default: 1=first=left)')

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    return parser.parse_args()

# ----------------------------------------------------------------------------


def audioextract():
    args = get_args_from_cmd()
    audio = aio_open(args.w)
    idx = audio.extract_channel(args.c - 1)

    # Save the converted channel
    audio_out = AudioPCM()
    audio_out.append_channel(audio.get_channel(idx))
    aio_save(args.o, audio_out)

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    audioextract()
