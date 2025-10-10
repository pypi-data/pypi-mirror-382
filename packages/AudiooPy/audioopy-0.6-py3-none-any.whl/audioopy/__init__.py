"""
:filename: audioopy.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Works easily with a recorded audio file.

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

from .audio import AudioPCM
from .audioframes import AudioFrames
from .audioconvert import AudioConverter
from .channel import Channel
from .channelframes import ChannelFrames
from .channelformatter import ChannelFormatter
from .channelsmixer import ChannelMixer
from .basevolume import BaseVolume
from .audiovolume import AudioVolume
from .channelvolume import ChannelVolume
import audioopy.ipus
import audioopy.aio

__author__ = "Brigitte Bigi"
__copyright__ = "Copyright (C) 2024-2025  Brigitte Bigi, CNRS, Laboratoire Parole et Langage, Aix-en-Provence, France"
__version__ = "0.6"
__all__ = [
    "AudioPCM",
    "AudioFrames",
    "AudioConverter",
    "Channel",
    "ChannelFrames",
    "ChannelFormatter",
    "ChannelMixer",
    "BaseVolume",
    "AudioVolume",
    "ChannelVolume"
]
