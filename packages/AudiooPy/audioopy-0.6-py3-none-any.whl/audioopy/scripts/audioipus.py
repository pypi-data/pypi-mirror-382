#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: audioopy.scripts.audioipus.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A script to search for IPUs from an audio file.

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

from audioopy.aio import open as aio_open
from audioopy.ipus import SearchForIPUs

# ----------------------------------------------------------------------------


def get_args_from_cmd():
    parser = ArgumentParser(usage="%s -w <input file> -o <output file> [options]" % os.path.basename(PROGRAM),
                            description="A script to search for Inter-Pausal Units (IPUs) from an audio file. "
                                        "IPUs are sound segments in speech. "
                                        "See <https://dx.doi.org/10.1007/978-3-031-05328-3_2> for details.")

    parser.add_argument("-w",
                        metavar="file",
                        required=True,
                        help='Audio input filename')

    parser.add_argument("-c",
                        metavar="value",
                        default=1,
                        type=int,
                        required=False,
                        help='Number of the channel to extract (default: 1=first=left)')

    parser.add_argument("-l",  # --win-length
                        metavar="value",
                        default=0.02,
                        type=float,
                        required=False,
                        help='Window size to estimate RMS (default: 0.02)')

    parser.add_argument("-t",  # --threshold
                        metavar="value",
                        default=0,
                        type=int,
                        required=False,
                        help='Threshold of the volume value (rms) for the detection of silences (default: 0=auto)')

    parser.add_argument("-d",  # --min_ipu
                        metavar="value",
                        default=0.3,
                        type=float,
                        required=False,
                        help='Minimum duration of an IPU (default: 0.300)')

    parser.add_argument("-s",  # --min_sil
                        metavar="value",
                        default=0.2,
                        type=float,
                        required=False,
                        help='Minimum duration of a silence (default: 0.200)')

    parser.add_argument("-b",  # --shift_start
                        metavar="value",
                        default=0.02,
                        type=float,
                        required=False,
                        help='Systematically shift the start boundary of an IPU to the left (default: 0.020)')

    parser.add_argument("-e",  # --shift_end
                        metavar="value",
                        default=0.02,
                        type=float,
                        required=False,
                        help='Systematically shift the end boundary of an IPU to the right  (default: 0.020)')

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    return parser.parse_args()


# ----------------------------------------------------------------------------


def audioipus():
    # Extract the audio channel
    args = get_args_from_cmd()
    audio = aio_open(args.w)
    idx = audio.extract_channel(args.c - 1)

    # Create an instance of the IPUs search object
    searcher = SearchForIPUs(channel=audio[idx])

    # Fix options
    searcher.set_vol_threshold(args.t)
    searcher.set_win_length(args.l)
    searcher.set_min_ipu(args.d)
    searcher.set_min_sil(args.s)
    searcher.set_shift_start(args.b)
    searcher.set_shift_end(args.e)

    # Process the data and get the list of IPUs
    tracks = searcher.get_tracks(time_domain=True)

    # Print result on stdout
    for i, track in enumerate(tracks):
        print(f"{track[0]}, {track[1]}, ipu_{i+1:03}")

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    audioipus()
