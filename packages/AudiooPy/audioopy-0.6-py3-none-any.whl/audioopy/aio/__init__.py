# -*- coding: UTF-8 -*-
"""
:filename: aio.__init__.py
:author: Brigitte Bigi
:contributor: Nicolas Chazeau
:contact: contact@sppas.org
:summary: Readers and writers of audio data.

.. _This file was initially part of SPPAS: <https://sppas.org>
.. _This file is now part of AudiooPy:
..
    ---------------------------------------------------------------------

    Copyright (C) 2024-2025  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    SPPAS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SPPAS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SPPAS. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    ---------------------------------------------------------------------

"""

from os.path import splitext

from ..audioopyexc import AudioIOError
from .audiofactory import AudioFactory
from .waveio import WaveIO

__all__ = ("WaveIO",)

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------


ext_wav = ['.wav', '.wave', '.[wWaAvV]', '.[wWaAvVeE]']

extensions = ['.wav', '.wave']
extensionsul = ext_wav

# ----------------------------------------------------------------------------


def get_extension(filename):
    return splitext(filename)[1][1:]

# ----------------------------------------------------------------------------
# Functions for opening and saving audio files.
# ----------------------------------------------------------------------------


def open(filename):
    """Open an audio file.

    :param filename: (str) the file name (including path)
    :raise: IOError, UnicodeError, Exception
    :return: sppasAudioPCM()

    >>> Open an audio file:
    >>> audio = audiodata.aio.open(filename)

    """
    ext = get_extension(filename).lower()
    aud = AudioFactory.new_audio_pcm(ext)
    try:
        aud.open(filename)
    except IOError as e:
        raise AudioIOError(message=str(e), filename=None)
    except EOFError:
        raise AudioIOError(message="Malformed file", filename=None)

    return aud

# ----------------------------------------------------------------------------


def save(filename, audio):
    """Write an audio file.

    :param filename: (str) the file name (including path)
    :param audio: (sppasAudioPCM) the Audio to write.
    :raises: IOError

    """
    ext = get_extension(filename).lower()
    output = AudioFactory.new_audio_pcm(ext)

    output.set(audio)
    output.save(filename)

# ----------------------------------------------------------------------------


def save_fragment(filename, audio, frames):
    """Write a fragment of frames of an audio file.

    :param filename: (str) the file name (including path)
    :param audio: (sppasAudioPCM) the Audio to write.
    :param frames: (str)
    :raises: IOError

    """
    ext = get_extension(filename).lower()
    output = AudioFactory.new_audio_pcm(ext)

    output.set(audio)
    output.save_fragment(filename, frames)
