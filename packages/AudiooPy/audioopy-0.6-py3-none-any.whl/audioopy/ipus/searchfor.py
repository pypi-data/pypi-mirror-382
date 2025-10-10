# -*- coding: UTF-8 -*-
"""
:filename: audioopy.ipus.searchfor.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Silences vs sounding segments segmentation.

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

from ..channel import Channel

from .channelsilences import ChannelSilences

# ---------------------------------------------------------------------------


class SearchForIPUs(ChannelSilences):
    """An automatic silence versus sounding segments segmentation system.

    This segmentation aims at finding IPUs - Inter-Pausal Units, also called
    sounding segments, in speech. IPUs are blocks of speech bounded by silent
    pauses of more than X ms, and time-aligned on the speech signal.

    See the following reference publication:

    > Brigitte Bigi, Béatrice Priego-Valverde (2022).
    > The automatic search for sounding segments of SPPAS: application to Cheese! corpus.
    > Human Language Technology. Challenges for Computer Science and Linguistics, LNAI,
    > LNCS 13212, pp. 16-27.
    > <https://hal.archives-ouvertes.fr/hal-03697808>

    """

    MIN_SIL_DUR = 0.06
    MIN_IPU_DUR = 0.06
    DEFAULT_MIN_SIL_DUR = 0.250
    DEFAULT_MIN_IPU_DUR = 0.300
    DEFAULT_VOL_THRESHOLD = 0
    DEFAULT_SHIFT_START = 0.02
    DEFAULT_SHIFT_END = 0.02

    def __init__(self, channel: Channel, win_len: float = 0.02):
        """Create a new SearchIPUs instance.

        The class is particularly useful for identifying segments of speech
        bounded by silent pauses.

        Fields:

        - _win_len (inherited): Window length for RMS estimation.
        - _vagueness (inherited): Windows length to refine the silence boundaries estimation.
        - _channel (inherited): Channel instance to use.
        - _min_sil_dur: Minimum duration for a silence.
        - _min_ipu_dur: Minimum duration for an IPU.
        - _vol_threshold: Volume threshold for silence detection.
        - _auto_threshold: Automatically estimated volume threshold for silence detection.
        - _shift_start: Start shift value.
        - _shift_end: End shift value.

        :param channel: (Channel)

        """
        super(SearchForIPUs, self).__init__(channel, win_len, win_len / 4.)

        self._min_sil_dur = SearchForIPUs.DEFAULT_MIN_SIL_DUR
        self._min_ipu_dur = SearchForIPUs.DEFAULT_MIN_IPU_DUR
        self._vol_threshold = SearchForIPUs.DEFAULT_VOL_THRESHOLD
        self._auto_threshold = SearchForIPUs.DEFAULT_VOL_THRESHOLD
        self._shift_start = SearchForIPUs.DEFAULT_SHIFT_START
        self._shift_end = SearchForIPUs.DEFAULT_SHIFT_END

    # -----------------------------------------------------------------------
    # Manage Channel
    # -----------------------------------------------------------------------

    def get_track_data(self, tracks: list) -> list:
        """Return the audio data of tracks.

        :param tracks: List of tracks. A track is a tuple (start, end).
        :return: List of audio data

        """
        return self.__track_data(tracks)

    # -----------------------------------------------------------------------
    # Getters for members
    # -----------------------------------------------------------------------

    def get_vol_threshold(self) -> int:
        """Return the initial volume threshold used to search for silences."""
        return self._vol_threshold

    def get_effective_threshold(self) -> int:
        """Return the threshold volume estimated automatically to search for silences."""
        return self._auto_threshold

    def get_min_sil_dur(self) -> float:
        """Return the minimum duration of a silence."""
        return self._min_sil_dur

    def get_min_ipu_dur(self) -> float:
        """Return the minimum duration of a track."""
        return self._min_ipu_dur

    def get_shift_start(self) -> float:
        return self._shift_start

    def get_shift_end(self) -> float:
        return self._shift_end

    # -----------------------------------------------------------------------
    # Setters for members
    # -----------------------------------------------------------------------

    def set_vol_threshold(self, vol_threshold: int) -> None:
        """Fix the default minimum volume value to find silences.

        It won't affect the current list of silence values. Use search_sil().

        :param vol_threshold: (int) RMS value

        """
        vol_threshold = int(vol_threshold)
        if vol_threshold < 0:
            self._vol_threshold = SearchForIPUs.DEFAULT_VOL_THRESHOLD
        else:
            self._vol_threshold = vol_threshold

    # -----------------------------------------------------------------------

    def set_min_sil(self, min_sil_dur: float) -> None:
        """Fix the default minimum duration of a silence.

        :param min_sil_dur: (float) Duration in seconds.
        :raises: ValueError: Invalid given min_sil_dur value.

        """
        min_sil_dur = float(min_sil_dur)
        self._min_sil_dur = max(float(min_sil_dur), SearchForIPUs.MIN_SIL_DUR)

    # -----------------------------------------------------------------------

    def set_min_ipu(self, min_ipu_dur: float) -> None:
        """Fix the default minimum duration of an IPU.

        :param min_ipu_dur: (float) Duration in seconds.
        :raises: ValueError: Invalid given min_ipu_dur value.

        """
        min_ipu_dur = float(min_ipu_dur)
        self._min_ipu_dur = max(min_ipu_dur, SearchForIPUs.MIN_IPU_DUR)

    # -----------------------------------------------------------------------

    def set_shift_start(self, s: float) -> None:
        """Fix the default minimum boundary shift value.

        :param s: (float) Duration in seconds.
        :raises: ValueError: Invalid given s value.

        """
        s = float(s)
        if -self._min_ipu_dur < s < self._min_sil_dur:
            self._shift_start = s

    # -----------------------------------------------------------------------

    def set_shift_end(self, s: float) -> None:
        """Fix the default minimum boundary shift value.

        :param s: (float) Duration in seconds.

        """
        s = float(s)
        if -self._min_ipu_dur < s < self._min_sil_dur:
            self._shift_end = s

    # -----------------------------------------------------------------------

    def min_channel_duration(self) -> float:
        """Return the minimum duration we expect for a channel."""
        d = max(self._min_sil_dur, self._min_ipu_dur)
        return d + self._shift_start + self._shift_end

    # -----------------------------------------------------------------------

    def get_rms_stats(self) -> list:
        """Return min, max, mean, median, stdev of the RMS."""
        vs = self.get_volstats()
        return [vs.min(), vs.max(), vs.mean(), vs.median(), vs.coefvariation()]

    # -----------------------------------------------------------------------
    # Silence/Speech segmentation
    # -----------------------------------------------------------------------

    def get_tracks(self, time_domain: bool = False) -> list:
        """Return a list of tuples (from,to) of tracks.

        (from,to) values are converted, or not, into the time-domain.

        The tracks are found from the current list of silences, which is
        firstly filtered with the min_sil_dur.

        Using this method requires the following members to be fixed:
            - the volume threshold
            - the minimum duration for a silence,
            - the minimum duration for a track,
            - the duration to remove to the start boundary,
            - the duration to add to the end boundary.

        :param time_domain: (bool) Convert from/to values in seconds
        :return: (list of tuples) with (from,to) of the tracks

        """
        # Search for the silences, comparing each rms to the threshold
        self._auto_threshold = self.search_silences(self._vol_threshold)

        # Keep only silences during more than a given duration
        # remove silences first because we are interested in finding tracks
        # The min sil value is taking into account the future shift values
        # applied to 'enlarge' the IPUs
        msd = self._min_sil_dur + self._shift_start + self._shift_end
        thr = self._auto_threshold // 2
        self.filter_silences(thr, msd)

        # Get the (from_pos, to_pos) of the tracks during more than
        # a given duration and shift these values (from-start; to+end)
        tracks = self.extract_tracks(self._min_ipu_dur, self._shift_start, self._shift_end)

        # Convert the (from_pos, to_pos) of tracks into (from_time, to_time)
        if time_domain is True:
            time_tracks = []
            for i, (from_pos, to_pos) in enumerate(tracks):
                f = float(from_pos) / float(self._channel.get_framerate())
                t = float(to_pos) / float(self._channel.get_framerate())
                time_tracks.append((f, t))
            return time_tracks

        return tracks

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __track_data(self, tracks: list) -> None:
        """Yield the tracks data: a set of frames for each track.

        :param tracks: (list of tuples) List of (from_pos,to_pos)
        :raises: TypeError: Invalid given tracks
        :raises: ValueError: Invalid frame position

        """
        if self._channel is None:
            return

        for v in tracks:
            try:
                if len(v) != 2:
                    raise
                int(v[0])
                int(v[1])
            except:
                raise TypeError('Expected a list of 2 int values, got {} instead'.format(v))

        nframes = self._channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
                else:
                    from_pos = nframes
            # Go to the provided position
            self._channel.seek(from_pos)
            # Keep in mind the related frames
            yield self._channel.get_frames(to_pos - from_pos)
