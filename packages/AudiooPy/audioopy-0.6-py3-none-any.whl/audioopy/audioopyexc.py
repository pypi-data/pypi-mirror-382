# -*- coding: UTF-8 -*-
"""
:filename: audioopy.audioopyexc.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Exceptions for the AudiooPy package.

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

from .po import tt

# -----------------------------------------------------------------------


class AudioError(Exception):
    """:ERROR 2000:.

    No audio file is defined.

    """

    def __init__(self):
        self.parameter = tt.error(2000)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioTypeError(TypeError):
    """:ERROR 2005:.

    Audio type error: not supported file format {extension}.

    """

    def __init__(self, extension):
        self.parameter = (tt.error(2005)).format(extension=extension)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class AudioIOError(IOError):
    """:ERROR 2010:.

    Opening, reading or writing error.

    """

    def __init__(self, message="", filename=""):
        self.parameter = (tt.error(2010)).format(filename=filename, message=message)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioDataError(Exception):
    """:ERROR 2015:.

    No data or corrupted data in the audio file {filename}.

    """

    def __init__(self, filename=""):
        self.parameter = (tt.error(2015)).format(filename=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ChannelIndexError(ValueError):
    """:ERROR 2020:.

    {number} is not a right index of channel.

    """

    def __init__(self, index):
        index = int(index)
        self.parameter = (tt.error(2020)).format(number=index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IntervalError(ValueError):
    """:ERROR 2025:.

    From {value1} to {value2} is not a proper interval.

    """

    def __init__(self, value1, value2):
        value1 = int(value1)
        value2 = int(value2)
        self.parameter = (tt.error(2025)).format(value1=value1, value2=value2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ChannelError(Exception):
    """:ERROR 2050:.

    No channel defined.

    """

    def __init__(self):
        self.parameter = tt.error(2050)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class MixChannelError(ValueError):
    """:ERROR 2060: :ERROR 2061: :ERROR 2062: :ERROR 2050: .

    Channels have not the same sample width.
    Channels have not the same frame rate.
    Channels have not the same number of frames.

    """

    def __init__(self, value=0):
        value = int(value)
        if value == 1:
            self.parameter = tt.error(2060)
        elif value == 2:
            self.parameter = tt.error(2061)
        elif value == 3:
            self.parameter = tt.error(2062)
        else:
            self.parameter = tt.error(2050)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SampleWidthError(ValueError):
    """:ERROR 2070:.

     Invalid sample width {value}.

     """

    def __init__(self, value):
        value = int(value)
        self.parameter = (tt.error(2070)).format(value=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class FrameRateError(ValueError):
    """:ERROR 2080:

    Invalid framerate {value}.

    """

    def __init__(self, value):
        value = int(value)
        self.parameter = (tt.error(2080)).format(value=value)

    def __str__(self):
        return repr(self.parameter)
# -----------------------------------------------------------------------


class NumberFramesError(Exception):
    """:ERROR 2090:.

     Not a whole number of frames: nframes={} is not a multiple of (size={} * nchannels={}).

     """

    def __init__(self, nframes, sampwidth, nchannels):
        self.parameter = (tt.error(2090)).format(nframes=nframes,
                                                 sampwidth=sampwidth,
                                                 nchannels=nchannels)

    def __str__(self):
        return repr(self.parameter)
