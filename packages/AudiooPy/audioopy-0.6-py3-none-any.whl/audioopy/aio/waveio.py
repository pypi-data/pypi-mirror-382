# -*- coding: UTF-8 -*-
"""
:filename: audioopy.aio.waveio.py
:author: Brigitte Bigi
:contributor: Nicolas Chazeau
:contact: contact@sppas.org
:summary: Microsoft WAV support.

.. _This file was initially part of SPPAS: <https://sppas.org>
.. _This file is now part of AudiooPy:
..
    ---------------------------------------------------------------------

    Copyright (C) 2024-2025  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

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
import wave

from ..audio import AudioPCM

# ---------------------------------------------------------------------------


class WaveIO(AudioPCM):
    """Opening and saving Waveform Audio File Format (WAV) files.

    It extends the AudioPCM class to provide functionality for opening and
    saving audio files in the Waveform Audio File Format (WAV).
    Waveform Audio File Format is a Microsoft and IBM audio file format
    standard for storing an audio bitstream on PCs. It is an application of
    the Resource Interchange File Format (RIFF) bitstream format method for
    storing data in "chunks".

    :example:
    >>> # Create an instance and open the WAV file
    >>> wave_io = WaveIO()
    >>> wave_io.open("input.wav")
    >>> # Save the audio content to a new WAV file
    >>> wave_io.save("output.wav")
    >>> # Save a fragment of the audio content to a new WAV file
    >>> frames = wave_io.read_frames(1000)
    >>> wave_io.save_fragment("fragment.wav", frames)

    """
    def __init__(self):
        """Create a WaveIO instance."""
        super(WaveIO, self).__init__()

    # -----------------------------------------------------------------------

    def open(self, filename: str) -> None:
        """Get an audio from a Waveform Audio File Format file.

        :param filename (str) input file name.
        :raises: wave.Error: if the file cannot be opened.

        """
        # Use the standard wave library to load the wave file
        # open method returns a Wave_read() object
        self._audio_fp = wave.open(filename, "r")

    # -----------------------------------------------------------------------

    def save(self, filename: str) -> None:
        """Write an audio content as a Waveform Audio File Format file.

        :param filename (str) output filename.

        """
        if self._audio_fp is not None:
            self.rewind()
            frames = self._audio_fp.readframes(self._audio_fp.getnframes())
            self.save_fragment(filename, frames)

        elif len(self._channels) == 1:
            channel = self._channels[0]
            f = wave.Wave_write(filename)
            f.setnchannels(1)
            f.setsampwidth(channel.get_sampwidth())
            f.setframerate(channel.get_framerate())
            try:
                f.writeframes(channel.get_frames())
            finally:
                f.close()

        else:
            self.verify_channels()
            sw = self._channels[0].get_sampwidth()
            frames = b""
            for i in range(0, self._channels[0].get_nframes()*sw, sw):
                for j in range(len(self._channels)):
                    frames += self._channels[j].get_frames(sw)

            f = wave.Wave_write(filename)
            f.setnchannels(len(self._channels))
            f.setsampwidth(self._channels[0].get_sampwidth())
            f.setframerate(self._channels[0].get_framerate())
            try:
                f.writeframes(frames)
            finally:
                f.close()

    # -----------------------------------------------------------------------

    def save_fragment(self, filename: str, frames: bytes) -> None:
        """Write an audio content as a Waveform Audio File Format file.

        :param filename: (str) output filename.
        :param frames: (bytes) the frames to write

        """
        f = wave.Wave_write(filename)
        f.setnchannels(self.get_nchannels())
        f.setsampwidth(self.get_sampwidth())
        f.setframerate(self.get_framerate())
        try:
            f.writeframes(frames)
        finally:
            f.close()
