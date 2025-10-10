# -*- coding: UTF-8 -*-
"""
:filename: audioopy.channelsilence.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Search for silences in frames of a channel.

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
import logging

from audioopy.channel import Channel
from audioopy.channelvolume import ChannelVolume

# ----------------------------------------------------------------------------


class ChannelSilences(object):
    """Silence search on a channel of an audio file.

    Silences are stored in a list of (from_pos,to_pos) values, indicating
    the frame from which each silence is starting and ending. The rms -
    root-mean-square, is estimated in windows of 10 ms by default. The silence
    versus sounding intervals are stamped depending on a rms threshold value.
    Consecutive silences then sounding intervals are then grouped and compared
    to given minimum durations allowing to get tracks.

    """

    MIN_WIN_LEN = 0.001
    MAX_WIN_LEN = 0.050

    def __init__(self, channel: Channel, win_len: float = 0.01, vagueness: float = 0.005):
        """Create a ChannelSilence instance.

        The duration of a window (win_len) is relevant for the estimation of the rms values.
        The maximum value of vagueness is win_len.

        :param channel: (Channel) Input channel object
        :param win_len: (float) Duration of a window for the estimation of the volume values
        :param vagueness: (float) Windows length to estimate the silence boundaries

        """
        # The audio data
        self._channel = None
        self._win_len = 0.01
        self.set_win_length(win_len)

        # Vagueness is used to estimate more precisely the track boundaries
        self._vagueness = min(float(vagueness), self._win_len)

        # The rms list of values
        self.__volume_stats = None
        # The list of founded silences
        self.__silences = list()
        # Set the channel, estimate volumes and reset silences
        if channel is not None:
            self.set_channel(channel)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_win_length(self) -> float:
        """Return the window length used to estimate the RMS."""
        return self._win_len

    # -----------------------------------------------------------------------

    def set_win_length(self, w: float) -> None:
        """Set a new length of window and perform estimation of volume values.

        It cancels any previous estimation of volume and silence search.

        :param w: (float) between 0.001 and 0.05.
        :raises: ValueError: if w is not a float

        """
        # Windows length for rms estimations
        win_len = float(w)
        if ChannelSilences.MIN_WIN_LEN <= win_len <= ChannelSilences.MAX_WIN_LEN:
            self._win_len = win_len
        elif win_len > ChannelSilences.MAX_WIN_LEN:
                self._win_len = ChannelSilences.MAX_WIN_LEN
        else:
            self._win_len = ChannelSilences.MIN_WIN_LEN

        if self._channel is not None:
            self.set_channel(self._channel)

    # -----------------------------------------------------------------------

    def get_vagueness(self) -> float:
        """Return the vagueness value."""
        return self._vagueness

    # -----------------------------------------------------------------------

    def set_vagueness(self, vagueness: float) -> None:
        """Fix the windows length to estimate the boundaries.

        :param vagueness: (float) Maximum value of vagueness is win_len.

        """
        vagueness = float(vagueness)
        if vagueness > 0.:
            self._vagueness = min(vagueness, self._win_len)
        else:
            self._vagueness = 0.

    # -----------------------------------------------------------------------

    def get_channel(self) -> Channel:
        """Return the channel."""
        return self._channel

    # -----------------------------------------------------------------------

    def set_channel(self, channel: Channel) -> None:
        """Set a channel, then reset all previous results.

        :param channel: (Channel) The channel to be used to search for silences
        :raises: TypeError: Given parameter is not a Channel

        """
        if isinstance(channel, Channel) is False:
            raise TypeError('Expected a Channel, got {:s} instead.'.format(str(type(channel))))

        self._channel = channel
        self.__volume_stats = ChannelVolume(channel, self._win_len)
        self.__silences = list()

    # -----------------------------------------------------------------------

    def get_volstats(self) -> ChannelVolume | None:
        """Return the RMS values estimated on the channel."""
        return self.__volume_stats

    # -----------------------------------------------------------------------

    def set_silences(self, silences: list) -> None:
        """Fix manually silences; to be use carefully.

        Assign manually the list of tuples (start, end) of each silence.

        :param silences: (list of tuples (start_pos, end_pos))
        :raises: TypeError: Invalid given parameter

        """
        # check if it's really a list or tuple
        if isinstance(silences, (list, tuple)) is False:
            raise TypeError('Expected a list, got {:s} instead'.format(str(type(silences))))

        for v in silences:
            if isinstance(v, (list, tuple)) is False:
                raise TypeError('Expected a list or tuple, got {:s} instead'.format(v))
            try:
                if len(v) != 2:
                    raise ValueError
                int(v[0])
                int(v[1])
            except ValueError:
                raise TypeError('Expected a list of 2 int values, got {} instead'.format(v))

        # ok, assign value
        self.__silences = silences

    # -----------------------------------------------------------------------

    def reset_silences(self) -> None:
        """Reset silences to an empty list."""
        self.__silences = list()

    # -----------------------------------------------------------------------
    # Utility methods
    # -----------------------------------------------------------------------

    def refine(self, pos: int, threshold: int, win_length: float = 0.005, direction: int = 1):
        """Improve the precision of the given position of a silence.

        :param pos: (int) Initial position of the silence
        :param threshold: (int) rms threshold value for a silence
        :param win_length: (float) Windows duration to estimate the rms
        :param direction: (int)
        :return: (int) updated position

        """
        delta = int(self.__volume_stats.get_winlen() * self._channel.get_framerate())
        from_pos = max(pos-delta, 0)
        self._channel.seek(from_pos)
        frames = self._channel.get_frames(delta*2)
        c = Channel(self._channel.get_framerate(), self._channel.get_sampwidth(), frames)
        vol_stats = ChannelVolume(c, win_length)

        if direction == 1:
            for i, v in enumerate(vol_stats):
                if v > threshold:
                    return from_pos + i*(int(win_length*self._channel.get_framerate()))
        if direction == -1:
            i = len(vol_stats)
            for v in reversed(vol_stats):
                if v > threshold:
                    return from_pos + (i*(int(win_length*self._channel.get_framerate())))
                i -= 1

        return pos

    # -----------------------------------------------------------------------

    def extract_tracks(self, min_track_dur: float, shift_dur_start: float, shift_dur_end: float):
        """Return the tracks, deduced from the silences and track constrains.

        :param min_track_dur: (float) The minimum duration for a track
        :param shift_dur_start: (float) The time to remove to the start bound
        :param shift_dur_end: (float) The time to add to the end boundary
        :return: list of tuples (from_pos,to_pos)

        Duration is in seconds.

        """
        if self._channel is None:
            return []

        tracks = list()

        # No silence: Only one track!
        if len(self.__silences) == 0:
            tracks.append((0, self._channel.get_nframes()))
            return tracks

        # Convert values from time to frames
        delta = int(min_track_dur * self._channel.get_framerate())
        shift_start = int(shift_dur_start * self._channel.get_framerate())
        shift_end = int(shift_dur_end * self._channel.get_framerate())
        from_pos = 0

        for to_pos, next_from in self.__silences:

            if (to_pos-from_pos) >= delta:
                # Track is long enough to be considered an IPU.
                # Apply the shift values
                shift_from_pos = max(from_pos - shift_start, 0)
                shift_to_pos = min(to_pos + shift_end, self._channel.get_nframes())
                # Store as it
                tracks.append((int(shift_from_pos), int(shift_to_pos)))

            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self._channel.get_nframes()
        if (to_pos - from_pos) >= delta:
            tracks.append((int(from_pos), int(to_pos)))

        return tracks

    # -----------------------------------------------------------------------
    # Silence detection
    # -----------------------------------------------------------------------

    def fix_threshold_vol(self) -> int:
        """Fix automatically the threshold for optimizing tracks/silences search.

        This is an observation of the distribution of rms values.

        :return: (int) volume value

        """
        # Get the statistics of the rms values
        vmin = max(self.__volume_stats.min(), 0)  # provide negative values
        vmean = self.__volume_stats.mean()
        vmedian = self.__volume_stats.median()
        vvar = self.__volume_stats.coefvariation()

        # Remove very high volume values (outliers), if any:
        # it's only for distributions with a too high variability
        if vmedian > vmean:
            logging.warning(' ... Due to un-expected outlier values, the automatic threshold estimation '
                            'requires the rms distribution to be normalized.')
            # Make a copy of the actual volume values and modify the copied instance
            vol_stats = ChannelVolume(self._channel, self._win_len)
            vol_stats.normalize_volumes()
            vmean = vol_stats.mean()
            vmedian = vol_stats.median()
            vvar = vol_stats.coefvariation()
            volumes = sorted(vol_stats.volumes())
        else:
            volumes = sorted(self.__volume_stats.volumes())

        logging.info("- rms min={:.2f}".format(vmin))
        logging.info("- rms mean={:.2f}".format(vmean))
        logging.info("- rms median={:2f}".format(vmedian))
        logging.info("- rms coef. var={:2f}".format(vvar))

        # Several alternatives in case the audio is not as good as expected -
        # - a too low volume or some outliers make the coeff var very high, or
        # the general case.
        vcvar = 1.5 * vvar
        if vmedian > vmean:
            # often means a lot of low volume values and some very high
            median_index = 0.55 * len(volumes)
            threshold = int(volumes[int(median_index)])
            logging.info(' ... Un-expected audio quality. Threshold with estimator exception 1 '
                         '- median > mean: {:d}'.format(threshold))
        elif vcvar > vmean:
            if vmedian < (vmean * 0.2):
                # for distributions with a too low variability
                threshold = int(vmin) + int((vmean - vmedian))
                logging.info(' ... Un-expected audio quality. Threshold with estimator exception 2 '
                             '- median < 0.2*mean: {:d}'.format(threshold))
            else:
                # often means some crazy values (very rare)
                threshold = int(vmin) + int(0.2 * float(vmean))
                logging.info(' ... Un-expected audio quality. Threshold with estimator exception 3 '
                             '- vcvar > mean: {:d}'.format(threshold))
        else:
            threshold = int(vmin) + int((vmean - vcvar))
            logging.info('Audio of expected quality. Threshold uses the normal estimator: {:d}'.format(threshold))

        return threshold

    # -----------------------------------------------------------------------

    def search_silences(self, threshold: int = 0) -> int:
        """Search windows with a volume lesser than a given threshold.

        This is then a search for silences. All windows with a volume
        higher than the threshold are considered as tracks and not included
        in the result. Block of silences lesser than min_sil_dur are
        also considered tracks.
        If threshold is set to 0, a value is automatically assigned.

        :param threshold: (int) Expected minimum volume (rms value).
        :return: (int) The actual threshold value

        """
        if self._channel is None:
            return 0

        if threshold == 0:
            threshold = self.fix_threshold_vol()

        # This scans the volumes whether it is lower than threshold,
        # and if true, it is written to silence.
        self.__silences = list()
        inside = False  # inside a silence or not
        idx_begin = 0
        nframes = self.__volume_stats.get_winlen() * self._channel.get_framerate()

        i = 0
        for v in self.__volume_stats:
            if v < threshold:
                # It's a small enough volume to consider the window a silence
                if inside is False:
                    # We consider it like the beginning of a block of silences
                    idx_begin = i
                    inside = True
                # else: it's the continuation of a silence
            else:
                # It's a big enough volume to consider the window an IPU
                if inside is True:
                    # It's the first window of a sounding segment
                    # so the previous window was the end of a silence
                    from_pos = int(idx_begin * nframes)
                    to_pos = int((i - 1) * nframes)
                    self.__silences.append((from_pos, to_pos))
                    inside = False
                # else: it's the continuation of a sounding segment
            i += 1

        # Last interval
        if inside is True:
            start_pos = int(idx_begin * self.__volume_stats.get_winlen() * self._channel.get_framerate())
            end_pos = self._channel.get_nframes()
            self.__silences.append((start_pos, end_pos))

        # Filter the current very small windows
        self.__filter_silences(2. * self._win_len)

        return threshold

    # -----------------------------------------------------------------------

    def filter_silences(self, threshold: int, min_sil_dur: float = 0.200) -> int:
        """Filter the current silences.

        :param threshold: (int) Expected minimum volume (rms value)
        :param min_sil_dur: (float) Minimum silence duration in seconds
        :return: (int) Number of silences with the expected minimum duration

        """
        if len(self.__silences) == 0:
            return 0

        if threshold == 0:
            threshold = self.fix_threshold_vol()

        # Adjust boundaries of the silences
        adjusted = list()
        for (from_pos, to_pos) in self.__silences:
            adjusted_from = self.__adjust_bound(from_pos, threshold, direction=-1)
            adjusted_to = self.__adjust_bound(to_pos, threshold, direction=1)
            adjusted.append((adjusted_from, adjusted_to))
        self.__silences = adjusted

        # Re-filter
        self.__filter_silences(min_sil_dur)

        return len(self.__silences)

    # -----------------------------------------------------------------------

    def filter_silences_from_tracks(self, min_track_dur: float = 0.60) -> None:
        """Filter the given silences to remove very small tracks.

        :param min_track_dur: (float) Minimum duration of a track

        """
        if len(self.__silences) < 3:
            return
        tracks = self.extract_tracks(min_track_dur, 0., 0.)

        # Remove too short tracks
        keep_tracks = list()
        for (from_track, to_track) in tracks:
            delta = float((to_track - from_track)) / float(self._channel.get_framerate())
            if delta > min_track_dur:
                keep_tracks.append((from_track, to_track))

        # Re-create silences from the selected tracks
        filtered_sil = list()
        # first silence
        if self.__silences[0][0] < keep_tracks[0][0]:
            filtered_sil.append((self.__silences[0][0], self.__silences[0][1]))
        # silences between tracks
        prev_track_end = -1
        for (from_track, to_track) in keep_tracks:
            if prev_track_end > -1:
                filtered_sil.append((int(prev_track_end), int(from_track)))
            prev_track_end = to_track
        # last silence
        to_pos = self._channel.get_nframes()
        to_track = tracks[-1][1]
        if (to_pos - to_track) > 0:
            filtered_sil.append((int(to_track), int(to_pos)))

        self.__silences = filtered_sil

    # -----------------------------------------------------------------------

    def __filter_silences(self, min_sil_dur: float = 0.200) -> None:
        """Filter the given silences.

        :param min_sil_dur: (float) Minimum silence duration in seconds

        """
        filtered_sil = list()
        for (start_pos, end_pos) in self.__silences:
            sil_dur = float(end_pos-start_pos) / float(self._channel.get_framerate())
            if sil_dur > min_sil_dur:
                filtered_sil.append((start_pos, end_pos))

        self.__silences = filtered_sil

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __adjust_bound(self, pos: int, threshold: int, direction: int = 0) -> int:
        """Adjust the position of a silence around a given position.

        Here "around" the position means in a range of 18 windows,
        i.e. 6 before + 12 after the given position.

        :param pos: (int) Initial position of the silence
        :param threshold: (int) RMS threshold value for a silence
        :param direction: (int)
        :return: (int) estimated position

        """
        if self._vagueness == self._win_len:
            return pos
        if direction not in (-1, 1):
            return pos

        # Extract the frames of the windows around the pos
        delta = int(1.5 * self.__volume_stats.get_winlen() * self._channel.get_framerate())
        start_pos = int(max(pos - delta, 0))
        self._channel.seek(start_pos)
        frames = self._channel.get_frames(int(delta * 3))

        # Create a channel and estimate volume values with a window
        # of vagueness (i.e. 4 times more precise than the original)
        c = Channel(self._channel.get_framerate(), self._channel.get_sampwidth(), frames)
        vol_stats = ChannelVolume(c, self._vagueness)

        # Can reduce the silence? the idea is to not miss low-level volume of the
        # beginning of the first phoneme or the end of the last one.
        new_pos = pos
        if direction == 1:  # silence | ipu
            # start to compare at the beginning of the silence: as soon as a rms value
            # is higher than the threshold, the silence ended.
            for idx, v in enumerate(vol_stats):
                shift = idx * (int(self._vagueness * self._channel.get_framerate()))
                if v > threshold:
                    new_pos = start_pos + int(shift)
                    break

        elif direction == -1:  # ipu | silence
            # start to compare at the end of the silence: as soon as a rms value is
            # higher than the threshold, the silence starts.
            idx = len(vol_stats)  # = 12 (3 windows of 4 vagueness)
            for v in reversed(vol_stats):
                if v >= threshold:
                    shift = idx * (int(self._vagueness * self._channel.get_framerate()))
                    new_pos = start_pos + int(shift)
                    break
                idx -= 1

        return new_pos

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__silences)

    def __iter__(self):
        for x in self.__silences:
            yield x

    def __getitem__(self, i):
        return self.__silences[i]
