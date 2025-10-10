# -*- coding: UTF-8 -*-
"""
:filename: audioopy.audioframes.py
:author: Brigitte Bigi
:contributor: Nicolas Chazeau
:contact: contact@sppas.org
:summary: Manipulate frames of an Audio()

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

import logging
import struct
import math
import wave

from .audioopyexc import NumberFramesError
from .audioopyexc import SampleWidthError
from .audioopyexc import ChannelIndexError
from .audioopyexc import FrameRateError

# ---------------------------------------------------------------------------


def gcd(a, b):
    """Return the greatest common divisor."""
    while b > 0:
        tmp = a % b
        a = b
        b = tmp
    return a

# ---------------------------------------------------------------------------


class AudioFrames(object):
    """A utility class for audio frames.

    Initially based on audioop (2011-2023), this class is self-implemented
    in 02-2024 due to PEP 594 (dead batteries). Actually, 'audioop' is one
    of the 19 removed libraries with no proposed alternative.

    :Example:
    >>> frames = b'\x01\x00\x02\x00\x03\x00\x04\x00'
    >>> a = AudioFrames(frames, sampwidth=2, nchannels=1)
    >>> a.rms()
    3
    >>> a.minmax()
    (1,5)

    Supported sample width is only either 1 (8bits) or 2 (16bits) or 4 (32bits).
    
    Note that operations such as rms() or mul() make no distinction between
    mono and stereo fragments, i.e. all samples are treated equal. If this is
    a problem the stereo fragment should be split into two mono fragments first
    and recombined later.

    """
    def __init__(self, frames=b"", sampwidth=2, nchannels=1):
        """Create an instance.

        :param frames: (str) input frames
        :param sampwidth: (int) sample width of the frames (1, 2 or 4)
        :param nchannels: (int) number of channels in the samples

        """
        # Check the type and if values are appropriate
        # frames = str(frames)
        sampwidth = int(sampwidth)
        if sampwidth not in [1, 2, 4]:
            raise SampleWidthError(sampwidth)
        nchannels = int(nchannels)
        if nchannels < 1:
            raise ChannelIndexError(nchannels)
        bytes_per_frame = sampwidth * nchannels
        if len(frames) % bytes_per_frame != 0:
            raise NumberFramesError(len(frames), sampwidth, nchannels)

        # Set data
        self._frames = frames
        self._sampwidth = sampwidth
        self._nchannels = nchannels

    # -----------------------------------------------------------------------

    def save(self, filename: str, framerate: int):
        """Save the audio frames to a file.

        :param filename: (str) output filename
        :param framerate: (int) frames per second

        """
        f = wave.Wave_write(filename)
        f.setnchannels(self.get_nchannels())
        f.setsampwidth(self.get_sampwidth())
        f.setframerate(framerate)
        try:
            f.writeframes(self._frames)
        finally:
            f.close()

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def get_minval(size, signed=True):
        """Return the min value for a given sampwidth.

        :param size: (int) the sampwidth
        :param signed: (bool) if the values will be signed or not
        :raise: SampleWidthError: Invalid given size.
        :return: (int) the min value

        """
        if not signed:
            return 0
        elif size == 1:
            return -0x80
        elif size == 2:
            return -0x8000
        elif size == 4:
            return -0x80000000

        raise SampleWidthError(size)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_maxval(size, signed=True):
        """Return the max value for a given sampwidth.

        :param size: (int) the sampwidth
        :param signed: (bool) if the values will be signed or not
        :raise: SampleWidthError: Invalid given size.
        :return: (int) the max value

        """
        if signed and size == 1:
            return 0x7f
        elif size == 1:
            return 0xff
        elif signed and size == 2:
            return 0x7fff
        elif size == 2:
            return 0xffff
        elif signed and size == 4:
            return 0x7fffffff
        elif size == 4:
            return 0xffffffff

        raise SampleWidthError(size)

    # -----------------------------------------------------------------------
    # Getters returning an information, i.e. a value.
    # -----------------------------------------------------------------------

    def get_nchannels(self):
        """Return the number of channels in the frames."""
        return self._nchannels

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        """Return the size of the frames in (1, 2, 4)."""
        return self._sampwidth

    # -----------------------------------------------------------------------

    def get_sample(self, i):
        """Return the value of given sample index.

        :param i: (int) index of the sample to get value
        :return: (int) value
        :raises: IndexError: Invalid sample index.

        """
        # Deprecated: return audioop.getsample(self._frames, self._sampwidth, int(i))
        start = i * self._sampwidth
        end = start + self._sampwidth
        if end > len(self._frames):
            raise IndexError("Sample index out of range")
        return self.__frame_to_sample(self._frames[start:end])

    # -----------------------------------------------------------------------

    def minmax(self):
        """Return the minimum and maximum values of all samples in the frames.

        :return: (int, int) Min and max amplitude values, or (0,0) if empty frames.

        """
        if len(self._frames) > 0:
            # Deprecated: return audioop.minmax(self._frames, self._sampwidth)
            val_min = self.get_maxval(self._sampwidth)
            val_max = self.get_minval(self._sampwidth)
            for i in range(len(self._frames) // self._sampwidth):
                val = self.get_sample(i)
                if val > val_max:
                    val_max = val
                if val < val_min:
                    val_min = val
            return val_min, val_max
        return 0, 0

    # -----------------------------------------------------------------------

    def min(self):
        """Return the minimum of the values of all samples in the frames."""
        # Deprecated: return audioop.minmax(self._frames, self._sampwidth)[0]
        return self.minmax()[0]

    # -----------------------------------------------------------------------

    def max(self):
        """Return the maximum of the values of all samples in the frames."""
        # Deprecated: return audioop.minmax(self._frames, self._sampwidth)[1]
        return self.minmax()[1]

    # -----------------------------------------------------------------------

    def absmax(self):
        """Return the maximum of the *absolute value* of all samples in the frames."""
        # Deprecated: return audioop.max(self._frames, self._sampwidth)
        val_min, val_max = self.minmax()
        return max(abs(val_min), abs(val_max))

    # -----------------------------------------------------------------------

    def avg(self):
        """Return the average over all samples in the frames.

        :return: (float) Average value rounded to 2 digits.

        """
        # Deprecated: return audioop.avg(self._frames, self._sampwidth)
        if len(self._frames) == 0:
            return 0
        samples_sum = 0.
        nb_samples = len(self._frames) / self._sampwidth
        for i in range(int(nb_samples)):
            samples_sum += self.get_sample(i)

        return round(samples_sum / nb_samples, 2)

    # -----------------------------------------------------------------------

    def rms(self):
        """Return the root-mean-square of the frames.

        :return: (float) sqrt(sum(S_i^2) / n) rounded to 2 digits

        """
        if len(self._frames) == 0:
            return 0.

        # Deprecated: return audioop.rms(self._frames, self._sampwidth)
        square_sum = 0.
        nb_samples = len(self._frames) / self._sampwidth
        for i in range(int(nb_samples)):
            val = self.get_sample(i)
            square_sum += (val*val)

        return round(math.sqrt(square_sum / nb_samples), 2)

    # -----------------------------------------------------------------------

    def cross(self):
        """Return the number of zero crossings in frames.

        :return: (int) Number of zero crossing or -1 if empty frames

        """
        # Deprecated: return audioop.cross(self._frames, self._sampwidth)
        n_cross = -1
        prev_val = 17  # Anything but 0 or 1.
        for i in range(len(self._frames) // self._sampwidth):
            # The sample is a negative value?
            val = self.get_sample(i) < 0
            # Compare to the previous sample value: if changed, there's a cross.
            if val != prev_val:
                n_cross += 1
            prev_val = val
        return n_cross

    # -----------------------------------------------------------------------

    def clip(self, factor=0.5):
        """Return the number of frames with a value higher than the one of the factor.

        :param factor: (float) All frames outside the interval are clipped.
        :return: (int)

        """
        max_val = int(AudioFrames.get_maxval(self._sampwidth) * float(factor))
        min_val = int(AudioFrames.get_minval(self._sampwidth) * float(factor))
        n_clip = 0
        for i in range(len(self._frames) // self._sampwidth):
            val = self.get_sample(i)
            if val >= max_val or val <= min_val:
                n_clip += 1
        return n_clip

    # -----------------------------------------------------------------------

    def clipping_rate(self, factor=0.5):
        """Return the clipping rate of the frames.

        Percentage of samples with a value higher than the one corresponding
        to the factor. Factor has to be between 0 and 1.

        :param factor: (float) All frames outside the interval are clipped.
        :return: (float) clipping rate value. To be multiplied by 100 to get the percentage!

        """
        if len(self._frames) == 0:
            return 0.
        return float(self.clip(factor)) / (len(self._frames) // self._sampwidth)

    # -----------------------------------------------------------------------
    # Getters returning frames, as bytes.
    # -----------------------------------------------------------------------

    def get_frames(self):
        """Return the stored frames."""
        return self._frames

    # -----------------------------------------------------------------------

    def byteswap(self):
        """Converts big-endian samples to little-endian and vice versa."""
        try:
            import audioop
            audioop.byteswap(self._frames, self._sampwidth)
            # is implemented as:
            #     for (i = 0; i < fragment->len; i += width) {
            #         int j;
            #         for (j = 0; j < width; j++)
            #             ncp[i + width - 1 - j] = ((unsigned char *)fragment->buf)[i + j];
            #     }
            #     return rv;
        except ModuleNotFoundError:
            raise NotImplementedError

    # -----------------------------------------------------------------------

    def findfactor(self, reference):
        """Return a factor F such that rms(add(mul(reference, -F))) is minimal.

        Estimates the factor with which you should multiply reference to make
        it match as well as possible to the frames.

        """
        try:
            import audioop
            audioop.findfactor(self._frames, reference)
            # is implemented as:
            #     cp1 = (const int16_t *)fragment->buf;
            #     cp2 = (const int16_t *)reference->buf;
            #     len = fragment->len >> 1;
            #     sum_ri_2 = _sum2(cp2, cp2, len);
            #     sum_aij_ri = _sum2(cp1, cp2, len);
            #     result = sum_aij_ri / sum_ri_2;
            #     return PyFloat_FromDouble(result);

        except ModuleNotFoundError:
            raise NotImplementedError

    # -----------------------------------------------------------------------

    def reverse(self):
        """Reverse the samples in the frames."""
        try:
            import audioop
            audioop.reverse(self._frames, self._sampwidth)
            # is implemented as:
            #    for (i = 0; i < fragment->len; i += width) {
            #        int val = GETRAWSAMPLE(width, fragment->buf, i);
            #        SETRAWSAMPLE(width, ncp, fragment->len - i - width, val);
            #    }
            #    return rv;
            #
        except ModuleNotFoundError:
            raise NotImplementedError

    # -----------------------------------------------------------------------

    def mul(self, factor):
        """Return frames for which all samples are multiplied by factor.

        All samples in the original frames are multiplied by the floating-point
        value factor. Samples are truncated in case of overflow.

        :param factor: (float) the factor which will be applied to each sample.
        :return: (bytes) converted frames

        """
        if len(self._frames) == 0:
            return b""
        factor = float(factor)
        # Deprecated: return audioop.mul(self._frames, self._sampwidth, factor)

        val_min = self.get_minval(self._sampwidth)
        val_max = self.get_maxval(self._sampwidth)
        mul_frames = self.__zero_frames()

        # Multiply each sample, providing clipping.
        for i in range(len(self._frames) // self._sampwidth):
            val = float(self.get_sample(i))
            mul_val = max(val_min, min(val_max, int(val * factor)))
            mul_frames[i] = self.__sample_to_frame(mul_val)

        return b"".join(mul_frames)

    # -----------------------------------------------------------------------

    def bias(self, value):
        """Return frames that is the original ones with a bias added to each sample.

        All samples in the original frames are summed with the given value.
        Samples are truncated in case of overflow.

        :param value: (int) the bias which will be applied to each sample.
        :return: (str) converted frames

        """
        if len(self._frames) == 0:
            return b""
        value = int(value)
        # Deprecated: return audioop.bias(self._frames, self._sampwidth, value)
        # Difference with our: audioop wraps around in case of overflow

        val_min = self.get_minval(self._sampwidth)
        val_max = self.get_maxval(self._sampwidth)
        mul_frames = self.__zero_frames()

        # Multiply each sample, providing clipping.
        for i in range(len(self._frames) // self._sampwidth):
            val = self.get_sample(i)
            mul_val = max(val_min, min(val_max, val + value))
            mul_frames[i] = self.__sample_to_frame(mul_val)

        return b"".join(mul_frames)

    # -----------------------------------------------------------------------

    def change_sampwidth(self, size):
        """Return frames with the given number of bytes.

        :param size: (int) new sample width of the frames.
            (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        :return: (bytes) converted frames

        """
        if size not in (1, 2, 4):
            raise SampleWidthError(size)
        # Deprecated: return audioop.lin2lin(self._frames, self._sampwidth, size)

        # List of '0' values
        zero_byte = b"\x00" * size
        size_frames = [zero_byte] * (len(self._frames) // self._sampwidth)

        # Get actual sample, and turn into a frame of new size
        for i in range(len(self._frames) // self._sampwidth):
            # Get sample and force it to 32 bits.
            val = self.get_sample(i)
            val = val << ((4 - self._sampwidth)*8)
            # Turn sample into the expected size and convert back to frames
            if size == 2:
                size_frames[i] = struct.pack("<h", val >> 16)
            elif size == 4:
                size_frames[i] = struct.pack("<l", val)
            elif size == 1:
                size_frames[i] = struct.pack("<b", val >> 24)

        return b"".join(size_frames)

    # -----------------------------------------------------------------------

    def resample(self, in_rate, out_rate=16000):
        """Return re-sampled frames with the given new framerate.

        :param in_rate: (int) The original sample rate of the audio frames
        :param out_rate: (int) The desired sample rate to resample the audio frames to
        :return: (bytes) the resampled audio frames.
        :raise: FrameRateError: invalid given in_rate
        :raise: FrameRateError: invalid given out_rate
        :raise: NotImplementedError: can't resample from in_rate to out_rate

        """
        if len(self._frames) == 0:
            return b""
        in_rate = int(in_rate)
        out_rate = int(out_rate)
        if in_rate < 8000:
            raise FrameRateError(in_rate)
        if out_rate < 8000:
            raise FrameRateError(out_rate)
        if in_rate == out_rate:
            return self._frames

        try:
            frames = self._re_sample(in_rate, out_rate)
            return frames
        except NotImplementedError as e:
            logging.warning("Deprecated. Since 'audioop' is removed of the Python standard library, "
                            "re-sampling is not fully available from Python 3.13. ")
            try:
                # Python < 3.13
                import audioop
                return audioop.ratecv(self._frames, self._sampwidth, self._nchannels, in_rate, out_rate, None)[0]
            except ModuleNotFoundError:
                raise e

    # -----------------------------------------------------------------------

    def _re_sample(self, in_rate, out_rate):
        """Do re-sampling, or not if in a not implemented condition.

        :param in_rate: (int) The original sample rate of the audio frames
        :param out_rate: (int) The desired sample rate to resample the audio frames to
        :return: (bytes) the resampled audio frames.

        """
        # ... from a sequence of in_n input samples, out_n will be generated.
        in_nsamples = len(self._frames) // self._sampwidth
        out_nsamples = math.ceil(float(len(self._frames)) / float(self._sampwidth) * float(out_rate) / float(in_rate))

        # Handle the case of empty input
        if in_nsamples == 0:
            return b""

        if AudioFrames._re_sample_valid_16kHz_rates(in_rate, out_rate) is False:
            frames_out = self._ratecv(in_rate, out_rate, in_nsamples, out_nsamples)
        else:
            frames_out = self._re_sample_for_down16kHz(in_rate, out_rate, in_nsamples, out_nsamples)

        return b"".join(frames_out)

    # -----------------------------------------------------------------------

    def _ratecv(self, in_rate, out_rate, in_nsamples, out_nsamples, state=None, weightA=1, weightB=0):
        """Interpolate input samples to produce output samples.

        This method is a python implementation of the audioop.ratecv function.
        This function adjusts the rate of audio samples by interpolating the samples
        from an input number of samples (in_nsamples) to an output number of samples
        (out_nsamples). It also performs a simple digital filter using the weights
        `weightA` and `weightB`.

        Known bug: the first frame is not properly interpolated.

        :param in_nsamples: (int) The total number of input samples
        :param out_nsamples: (int) The desired number of output samples
        :return: (list of bytes) Resampled audio frames

        """
        if in_rate*out_rate*in_nsamples*out_nsamples == 0:
            raise ValueError("Unexpected zero rate.")
        # Validate input parameters
        if weightA < 1 or weightB < 0:
            raise ValueError("weightA should be >= 1, weightB should be >= 0")

        # Divide in_rate and out_rate by their greatest common divisor. But do not overflow.
        gcd_rates = gcd(in_rate, out_rate)
        in_n = in_rate // gcd_rates
        in_nsamples = min(in_n, in_nsamples)
        out_n = out_rate // gcd_rates
        out_nsamples = min(out_n, out_nsamples)

        # Calculate the number of bytes per frame and the fragment length
        bytes_per_frame = self._sampwidth * self._nchannels
        if len(self._frames) % bytes_per_frame != 0:
            raise ValueError("Fragment is not a whole number of frames")
        num_frames = len(self._frames) // bytes_per_frame

        # Initialize the state (if provided)
        if state is None:
            prev_i = [0] * self._nchannels
            cur_i = [0] * self._nchannels
        else:
            if not isinstance(state, tuple):
                raise TypeError("State must be a tuple or None")
            if len(state) != self._nchannels:
                raise ValueError("State tuple size must match number of channels")
            prev_i, cur_i = zip(*state)
            prev_i = list(prev_i)
            cur_i = list(cur_i)

        # Calculate the output length based on the frame rates
        output_length = math.ceil(num_frames * out_nsamples / in_nsamples)
        zero_byte = b"\x00" * self._sampwidth
        output_frames = [zero_byte] * output_length

        # Process the frames
        input_idx = 0
        output_idx = 0
        # d_accumulator = -out_nsamples  # 'audioop' solution but one frame is missing in the result
        # d_accumulator = 0              # one extra frame in the result
        d_accumulator = -in_nsamples

        while input_idx < num_frames:
            # Update state and interpolate samples
            while d_accumulator < 0:
                for chan in range(self._nchannels):
                    prev_i[chan] = cur_i[chan]
                    first_frame = input_idx * bytes_per_frame
                    last_frame = input_idx * bytes_per_frame + (chan+1) * self._sampwidth
                    frame = self._frames[first_frame:last_frame]
                    try:
                        if len(frame) > 0:
                            cur_i[chan] = self.__frame_to_sample(frame)
                            # Simple filtering: implements a simple digital filter
                            cur_i[chan] = (weightA * cur_i[chan] + weightB * prev_i[chan]) // (weightA + weightB)
                    except:
                        pass
                input_idx += 1
                d_accumulator += out_nsamples

            while d_accumulator >= 0:
                for chan in range(self._nchannels):
                    # Linear interpolation of samples
                    val = round((prev_i[chan] * d_accumulator + cur_i[chan] * (out_nsamples - d_accumulator)) / out_nsamples)
                    # output_frames.append(self.__sample_to_frame(val))
                    try:
                        output_frames[output_idx] = self.__sample_to_frame(val)
                    except IndexError:
                        pass
                    output_idx += 1
                d_accumulator -= in_n

        return output_frames

    # -----------------------------------------------------------------------

    @staticmethod
    def _re_sample_valid_16kHz_rates(in_rate, out_rate):
        """Check if given frame rates are supported for simple re-sampling.

        :return: (bool) False if interpolation needed

        """
        if in_rate < out_rate:
            return False
        if out_rate != 16000:
            return False
        if in_rate not in (192000, 96000, 48000, 32000, 16000):
            return False
        return True

    # -----------------------------------------------------------------------

    def _re_sample_for_down16kHz(self, in_rate, out_rate, in_nsamples, out_nsamples):
        """Do re-sampling to 16kHz from a multiple.

        Get actual frames, turn into samples, and reduce into the new expected
        number of samples. Implemented solution algorithm is:

        1. add "in_n" samples into a buffer from frames;
        2. reduce the buffer to "out_n" samples;
        3. Go to 1. until the end of the frames is reached.

        :param in_rate: (int) The original sample rate of the audio frames
        :param out_rate: (int) The desired sample rate to resample the audio frames to (expected 16kHz)
        :param in_nsamples: (int) The number of samples required for re-sampling
        :param out_nsamples: (int) The number of re-sampled samples
        :return: (bytes) the resampled audio frames.

        """
        # Divide in_rate and out_rate by their greatest common divisor. But do not overflow.
        gcd_rates = gcd(in_rate, out_rate)
        in_n = in_rate // gcd_rates
        in_n = min(in_n, in_nsamples)
        out_n = out_rate // gcd_rates
        out_n = min(out_n, out_nsamples)

        # Create the output list of frames, filled with 0 values.
        zero_byte = b"\x00" * self._sampwidth
        size_frames = [zero_byte] * out_nsamples

        # Get actual sample(s), and reduce into the new expected nb of samples.
        # Implemented solution:
        #   - add "in_n" samples into a buffer from frames, then, reduce the buffer to "out_n" samples.
        #   - do it again until the end of the frames is reached.
        in_buffer = [0] * in_n
        cur_n = 0
        i = 0
        while i < in_nsamples:
            # Fill-in buffer. Get sample from frames.
            in_buffer[cur_n] = self.get_sample(i)
            cur_n = cur_n + 1
            i = i + 1

            # It's time to down-sample the content of the buffer.
            if cur_n == in_n or i == in_nsamples:
                if cur_n == in_n and in_n % out_n == 0:
                    # The input buffer is full.
                    out_buffer = self._down_sample(in_buffer, out_n)
                else:
                    # if not enough initial number of samples
                    while in_n % out_n != 0:
                        in_n += 1
                        in_buffer.append(in_buffer[cur_n - 1])
                    # It's not a full buffer because it's the last one.
                    while cur_n < in_n:
                        in_buffer[cur_n] = in_buffer[cur_n-1]
                        cur_n = cur_n + 1
                        i = i + 1
                    out_buffer = self._down_sample(in_buffer, out_n)
                # Store the content of down_buffer into the new list of frames
                for x in range(len(out_buffer)):
                    val = out_buffer[x]
                    size_frames[(i//in_n)-1+x] = self.__sample_to_frame(val)

                cur_n = 0

        return size_frames

    # -----------------------------------------------------------------------

    @staticmethod
    def _down_sample(samples, n):
        """Reduce the given samples to n items.

        Down-sample is not applicable if not len(samples) % n.

        :param samples: (list) List of sample values
        :param n: number of expected sample values in the returned list
        :return: (list) reduced list of samples

        """
        if len(samples) % n == 0:
            down = [0] * n
            # One sample over x is kept. No approximation needed.
            step = len(samples) // n
            buffer = list()
            cur = 0
            for i in range(len(samples) + 1):
                if len(buffer) == step:
                    # Full buffer is full.
                    # --> interpolation method is 'average' ...
                    down[cur] = int(sum(buffer) / len(buffer))
                    buffer = list()
                    cur = cur + 1
                if i < len(samples):
                    buffer.append(samples[i])
        else:
            raise NotImplementedError("Down-sample is not applicable {:d}%{:d} != 0."
                                      "".format(len(samples), n))
        return down

    # -----------------------------------------------------------------------
    # Private.
    # -----------------------------------------------------------------------

    def __frame_to_sample(self, frame):
        """Unpack a frame into its sample value.

        Make no distinction between mono and stereo frames.

        :param frame: (bytes) Frames with a length equal to the sample width (1, 2 or 4).
        :raise: SampleWidthError: if len(frame) != sample width
        :return: (int) value or 0

        """
        if self._sampwidth == 2 and len(frame) == 2:
            return struct.unpack("<%uh" % 1, frame)[0]
        elif self._sampwidth == 1 and len(frame) == 1:
            return struct.unpack("<%ub" % 1, frame)[0]
        elif self._sampwidth == 4 and len(frame) == 4:
            return struct.unpack("<%ul" % 1, frame)[0]
        raise SampleWidthError(len(frame))

    # -----------------------------------------------------------------------

    def __sample_to_frame(self, sample):
        """Pack a sample value into a frame.

        Make no distinction between mono and stereo frames.

        :param sample: Sample value
        :return: (bytes) Frame

        """
        if isinstance(sample, int) is False:
            raise TypeError("Given sample must be an integer. Got {}".format(type(sample)))
        if self._sampwidth == 2:
            return struct.pack("<h", sample)
        elif self._sampwidth == 4:
            return struct.pack("<l", sample)
        elif self._sampwidth == 1:
            return struct.pack("<b", sample)
        return b""

    # -----------------------------------------------------------------------

    def __zero_frames(self):
        """Return a list of frames with 0 bytes values."""
        zero_byte = b"\x00" * self._sampwidth
        return [zero_byte] * (len(self._frames) // self._sampwidth)

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._frames) // self._sampwidth
