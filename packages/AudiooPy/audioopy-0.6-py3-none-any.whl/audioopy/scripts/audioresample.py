#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: audioopy.scripts.audioresample.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A script to change framerate of an audio file.

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

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
AUDIOOPY = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.insert(0, AUDIOOPY)

import audioopy.aio
from audioopy import AudioFrames

# ----------------------------------------------------------------------------


def get_args_from_cmd():
    """Get args from the command-line interface with ArgumentParser."""
    parser = ArgumentParser(usage="%s -w file [options]" % os.path.basename(PROGRAM),
                            description="... a script to resample an audio file.")

    parser.add_argument("-w",
                        metavar="file",
                        required=True,
                        help='Input audio file name')

    parser.add_argument("-r",
                        metavar="value",
                        default=16000,
                        type=int,
                        help='Framerate (default: 16000)')

    parser.add_argument("-o",
                        metavar="file",
                        required=True,
                        help='Output audio filename')

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    return parser.parse_args()

# ---------------------------------------------------------------------------


def audioresample():

    args = get_args_from_cmd()
    audio = audioopy.aio.open(args.w)
    frames = audio.read_frames(audio.get_nframes())

    # Create an AudioFrames() allowing to manipulate frames of an audio
    resampled_frames = AudioFrames(frames).resample(in_rate=audio.get_framerate(), out_rate=args.r)

    # Save resampled frames
    AudioFrames(resampled_frames).save(args.o, args.r)

# ----------------------------------------------------------------------------


if __name__ == "__main__":
    audioresample()
