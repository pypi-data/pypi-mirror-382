import scipy.signal, numpy as np
import matplotlib.pyplot as plt
import lmfit, tempfile
# from lmfit import Parameters, fit_report, minimize
# from skimage.morphology import closing, square
from numpy import arcsin, sin, pi
from matplotlib.lines import Line2D
import math, re, os, sys, itertools
import sox
from subprocess import Popen, PIPE
from pathlib import Path
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
}) # for sox  "output file already exists and will be overwritten on build"
from datetime import datetime, timezone, timedelta
from collections import deque
from loguru import logger
from skimage.morphology import closing, erosion, remove_small_objects
from skimage.measure import regionprops, label
import ffmpeg, shutil
from rich import print
from rich.console import Console
# from rich.text import Text
from rich.table import Table
try:
    from . import device_scanner
except:
    import device_scanner

TEENSY_MAX_LAG = 1.01*128/44100 # sec, duration of a default length audio block

# see extract_seems_TicTacCode() for duration criterion values

CACHING = True
DEL_TEMP = False
MAXDRIFT = 15e-3 # in sec, for end of clip


################## pasted from FSKfreqCalculator.py output:
F1 = 630.00 # Hertz
F2 = 1190.00 # Hz , both from FSKfreqCalculator output
SYMBOL_LENGTH = 14.286 # ms, from FSKfreqCalculator.py
N_SYMBOLS = 35 # including sync pulse
##################

MINIMUM_LENGTH = 8 # sec
TRIAL_TIMES = [ # in seconds
            (3.5, -2),
            (3.5, -3.5),
            (3.5, -5),
            (2, -2),
            (2, -3.5),
            (2, -5),
            (0.5, -2),
            (0.5, -3.5),
            ]
SOUND_EXTRACT_LENGTH = (10*SYMBOL_LENGTH*1e-3 + 1) # second
SYMBOL_LENGTH_TOLERANCE = 0.07 # relative
FSK_TOLERANCE = 60 # Hz
SAMD21_LATENCY = 63 # microseconds, for DAC conversion
YEAR_ZERO = 2021


BPF_LOW_FRQ, BPF_HIGH_FRQ = (0.5*F1, 2*F2)


# utility for accessing pathnames
def _pathname(tempfile_or_path):
    if isinstance(tempfile_or_path, type('')):
        return tempfile_or_path ################################################
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path) ###########################################
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name ###########################################
    else:
        raise Exception('%s should be Path or tempfile... is %s'%(
            tempfile_or_path,
            type(tempfile_or_path)))

# for skimage.measure.regionprops
def _width(region):
    _,x1,_,x2 = region.bbox
    return x2-x1


def to_precision(x,p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """
    x = float(x)
    if x == 0.:
        return "0." + "0"*(p-1) ################################################
    out = []
    if x < 0:
        out.append("-")
        x = -x
    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)
    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)
    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1
    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1
    m = "%.*g" % (p, n)
    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)

class Decoder:
    """
    Object encapsulating DSP processes to demodulate TicTacCode track from audio
    file; Decoders are instantiated by their respective Recording object.
    Produces plots on demand for diagnostic purposes.

    Attributes:

        sound_extract : 1d numpy.ndarray of int16
            length determined by SOUND_EXTRACT_LENGTH (sec). Could be anywhere
            in the audio file (start, end, etc...) Set by Recording object.
            This audio signal might or might not be the TicTacCode track.
    
        sound_extract_position : int
            where the sound_extract is located in the file, samples
    
        samplerate : int
            sound sample rate, set by Recording object.

        rec : Recording
            recording on which the decoder is working
    
        effective_word_duration : float
            duration of a word, influenced by ucontroller clock

        pulse_detection_level : float
            level used to detect sync pulse

        silent_zone_indices : tuple of ints
            silent zone boundary positions relative to the start
            of self.sound_extract.
    
        estimated_pulse_position : int
            pulse position (samples) relative to the start of self.sound_extract

        detected_pulse_position : int
            pulse position (samples) relative to the start of self.sound_extract
    
    """

    def __init__(self, aRec, do_plots):
        """
        Initialises Decoder

        Returns
        -------
        an instance of Decoder.

        """
        self.rec = aRec
        self.do_plots = do_plots
        self.clear_decoder()


    def clear_decoder(self):
        self.sound_data_extract = None
        self.pulse_detection_level = None
        self.detected_pulse_position = None
        
    def set_sound_extract_and_sr(self, sound_extract, samplerate, sound_extract_position):
        """
        Sets:
            self.sound_extract -- mono data of short duration
            self.samplerate -- in Hz
            self.sound_extract_position -- position in the whole file

        Computes and sets:
            self.pulse_detection_level
            self.sound_extract_one_bit
            self.words_props (contains the sync pulse too)

        Returns nothing
        """
        logger.debug('sound_extract: %s, samplerate: %s Hz, sound_extract_position %s'%(
                sound_extract, samplerate, sound_extract_position))
        if len(sound_extract) == 0:
            logger.error('sound extract is empty, is sound track duration OK?')
            raise Exception('sound extract is empty, is sound track duration OK?')
        self.sound_extract_position = sound_extract_position
        self.samplerate = samplerate
        self.sound_extract = sound_extract
        self.pulse_detection_level = np.std(sound_extract)/4
        logger.debug('pulse_detection_level %f'%self.pulse_detection_level)
        bits = np.abs(sound_extract)>self.pulse_detection_level
        N_ones = round(1.5*SYMBOL_LENGTH*1e-3*samplerate) # so it includes sync pulse
        self.sound_extract_one_bit = closing(bits, np.ones(N_ones))
        if self.do_plots:
            self._plot_extract()
        logger.debug('sound_extract_one_bit len %i'%len(self.sound_extract_one_bit))
        self.words_props = regionprops(label(np.array(2*[self.sound_extract_one_bit]))) # new

    def extract_seems_TicTacCode(self):
        """        
        Determines if signal in sound_extract seems to be TTC.

        Uses the conditions below:

            Extract duration is 1.143 s. (ie one sec + 1 symbol duration)
            In self.word_props (list of morphology.regionprops):
                if one region, duration should be in [0.499 0.512] sec
                if two regions, total duration should be in [0.50 0.655]

        Returns True if self.sound_data_extract seems TicTacCode
        """
        failing_comment = '' # used as a flag
        props = self.words_props
        if len(props) not in [1,2]:
            failing_comment = 'len(props) not in [1,2]: %i'%len(props)
        else:
            logger.debug('len(props), %i, is in [1,2]'%len(props))
        if len(props) == 1:
            logger.debug('one region')
            w = _width(props[0])/self.samplerate
            # self.effective_word_duration = w
            # logger.debug('effective_word_duration %f (one region)'%w)
            if not 0.499 < w < 0.512: # TODO: move as TOP OF FILE PARAMS
                failing_comment = '_width %f not in [0.499 0.512]'%w
            else:
                logger.debug('0.499 < width < 0.512, %f'%w)
        else: # 2 regions
            logger.debug('two regions')
            widths = [_width(p)/self.samplerate for p in props] # in sec
            total_w = sum(widths)
            # extra_window_duration = SOUND_EXTRACT_LENGTH - 1
            # eff_w = total_w - extra_window_duration
            # logger.debug('effective_word_duration %f (two regions)'%eff_w)
            if not 0.5 < total_w < 0.656:
                failing_comment = 'two regions duration %f not in [0.50 0.655]\n%s'%(total_w, widths)
                # fig, ax = plt.subplots()
                # p(ax, sound_extract_one_bit)
            else:
                logger.debug('0.5 < total_w < 0.656, %f'%total_w)
        logger.debug('failing_comment: %s'%(
            'none' if failing_comment=='' else failing_comment))
        return failing_comment == '' # no comment = extract seems TicTacCode

    def _plot_extract(self):
        fig, ax = plt.subplots()
        start = self.sound_extract_position
        i_samples = np.arange(start, start + len(self.sound_extract))
        yt = ax.get_yaxis_transform()
        ax.hlines(0, 0, 1,
            transform=yt, alpha=0.3,
        linewidth=2, colors='black')
        ax.plot(i_samples, self.sound_extract, marker='o', markersize='1',
            linewidth=1.5,alpha=0.3, color='blue' )
        ax.plot(i_samples, self.sound_extract_one_bit*np.max(np.abs(self.sound_extract)), 
            marker='o', markersize='1',
            linewidth=1.5,alpha=0.3,color='red')
        xt = ax.get_xaxis_transform()
        ax.hlines(self.pulse_detection_level, 0, 1,
            transform=yt, alpha=0.3,
        linewidth=2, colors='green')
        custom_lines = [
            Line2D([0], [0], color='green', lw=2),
            Line2D([0], [0], color='blue', lw=2),
            Line2D([0], [0], color='red', lw=2),
            ]
        ax.legend(
            custom_lines,
            'detection level, signal, detected region'.split(','),
            loc='lower right')
        ax.set_title('Finding word + sync pulse')
        plt.xlabel("Position in file %s (samples)"%self.rec)
        plt.show()

    def get_time_in_sound_extract(self):
        """        
        Tries to decode time present in self.sound_extract, if successfull
        return a time dict, eg:{'version': 0, 'seconds':
        44, 'minutes': 57, 'hours': 19,
        'day': 1, 'month': 3, 'year offset': 1, 
        'pulse at': 670451.2217 } otherwise return None
        """
        pulse_detected = self._detect_sync_pulse_position()
        if not pulse_detected:
            return None
        symbols_data = self._get_symbols_data()
        frequencies = [self._get_main_frequency(data_slice)
                            for data_slice in symbols_data ]
        logger.debug('found frequencies %s'%frequencies)
        def _get_bit_from_freq(freq):
            mid_FSK = 0.5*(F1 + F2)
            return '1' if freq > mid_FSK else '0'
        bits = [_get_bit_from_freq(f) for f in frequencies]
        bits_string = ''.join(bits)
        logger.debug('giving bits:  LSB %s MSB'%bits_string)

        def _values_from_bits(bits):
            word_payload_bits_positions = {
                # start, finish (excluded)
                'version':(0,3), # 3 bits
                'seconds':(3,9), # 6 bits
                'minutes':(9,15),
                'hours':(15,20),
                'day':(20,25),
                'month':(25,29),
                'year offset':(29,34),
                }
            binary_words = { key : bits[slice(*value)]
                    for key, value 
                    in word_payload_bits_positions.items()
                    }
            int_values = { key : int(''.join(reversed(val)),2)
                    for key, val in binary_words.items()
                    }
            return int_values
        time_values = _values_from_bits(bits_string)
        logger.debug(' decoded time %s'%time_values)
        sync_pos_in_file = self.detected_pulse_position + \
                    self.sound_extract_position
        time_values['pulse at'] = sync_pos_in_file
        if not 0 <= time_values['seconds'] <= 59:
            return None
        if not 0 <= time_values['minutes'] <= 59:
            return None
        if not 0 <= time_values['hours'] <= 23:
            return None
        if not 1 <= time_values['month'] <= 12:
            return None
        return time_values
    
    def _detect_sync_pulse_position(self):
        # sets self.detected_pulse_position, relative to sound_extract
        #
        regions = self.words_props # contains the sync pulse too
        # len(self.words_props) should be 1 or 2 for vallid TTC
        logger.debug('len() of words_props: %i'%len(self.words_props))
        whole_region = [p for p in regions if 0.499 < _width(p)/self.samplerate < 0.512]
        logger.debug('region widths %s'%[_width(p)/self.samplerate for p in regions])
        logger.debug('number of whole_region %i'%len(whole_region))
        if len(regions) == 1 and len(whole_region) != 1:
            # oops
            logger.debug('len(regions) == 1 and len(whole_region) != 1, failed')
            return False #######################################################
        if len(whole_region) > 1:
            print('error in _detect_sync_pulse_position: len(whole_region) > 1 ')
            return False #######################################################
        if len(whole_region) == 1:
            # sync pulse at the begining of this one
            _, spike, _, _ = whole_region[0].bbox
        else:
            # whole_region is [] (all fractionnal) and
            # sync pulse at the begining of the 2nd region
            _, spike, _, _ = regions[1].bbox
            # but check there is still enough place for ten bits: 
            # 6 for secs + 3 for revision + blanck after sync
            minimum_samples = int(self.samplerate*10*SYMBOL_LENGTH*1e-3)
            whats_left = len(self.sound_extract) - spike
            if whats_left < minimum_samples:
                spike -= self.samplerate
                # else: stay there, will decode seconds in whats_left
        half_symbol_width = int(0.5*1e-3*SYMBOL_LENGTH*self.samplerate) # samples
        left, right = (spike - half_symbol_width, spike+half_symbol_width)
        spike_data = self.sound_extract[left:right]
        biggest_positive = np.max(spike_data)
        biggest_negative = np.min(spike_data)
        if abs(biggest_negative) > biggest_positive:
            # flip
            spike_data = -1 * spike_data
        def fit_line_until_negative():
            import numpy as np
            start = np.argmax(spike_data)
            xs = [start]
            ys = [spike_data[start]]
            i = 1
            while spike_data[start - i] > 0 and start - i >= 0:
                xs.append(start - i)
                ys.append(spike_data[start - i])
                i += 1
            # ax.scatter(xs, ys)
            import numpy as np
            coeff = np.polyfit(xs, ys, 1)
            m, b = coeff
            zero = int(-b/m)
            # check if data is from USB audio and tweak
            y_fit = np.poly1d(coeff)(xs)
            err = abs(np.sum(np.abs(y_fit-ys))/np.mean(ys))
            logger.debug('fit error for line in ramp: %f'%err)
            if err < 0.01: #good fit so not analog
                zero += 1
            return zero
        sync_sample = fit_line_until_negative() + left
        logger.debug('sync pulse found at %i in extract, %i in file'%(
                        sync_sample, sync_sample + self.sound_extract_position))
        self.detected_pulse_position = sync_sample
        return True
    
    def _get_symbols_data(self):
        # part of extract AFTER sync pulse
        whats_left = len(self.sound_extract) - self.detected_pulse_position # in samples
        whats_left /= self.samplerate # in sec
        whole_word_is_in_extr = whats_left > 0.512 
        if whole_word_is_in_extr:
            # one region
            logger.debug('word is in one sole region')
            length_needed = round(0.5*self.samplerate)
            length_needed += round(self.samplerate*SYMBOL_LENGTH*1e-3)
            whole_word = self.sound_extract[self.detected_pulse_position:
                                           self.detected_pulse_position + length_needed]
        else:
            # Two regions.
            logger.debug('word is in two regions, will wrap past seconds')
            # Consistency check: if not whole_word_is_in_extr
            # check has been done so seconds are encoded in what s left
            minimum_samples = round(self.samplerate*10*SYMBOL_LENGTH*1e-3)
            if whats_left*self.samplerate < minimum_samples:
                print('bug in _get_data_symbol():')
                print(' whats_left*self.samplerate < minimum_samples')
            # Should now build a whole 0.5 sec word by joining remaining data
            # from previous second beep
            left_piece = self.sound_extract[self.detected_pulse_position:]
            one_second_before_idx = round(len(self.sound_extract) - self.samplerate)
            length_needed = round(0.5*self.samplerate - len(left_piece))
            length_needed += round(self.samplerate*SYMBOL_LENGTH*1e-3)
            right_piece = self.sound_extract[one_second_before_idx:
                                            one_second_before_idx + length_needed]
            whole_word = np.concatenate((left_piece, right_piece))
            logger.debug('two chunks lengths: %i %i samples'%(len(left_piece),
                                                        len(right_piece)))
        # search for word start (some jitter because of Teensy Audio Lib)
        symbol_length = round(self.samplerate*SYMBOL_LENGTH*1e-3)
        start = round(0.5*symbol_length) # half symbol
        end = start + symbol_length
        word_begining = whole_word[start:]
        gt_detection_level = np.argwhere(np.abs(word_begining)>self.pulse_detection_level)
        word_start = gt_detection_level[0][0]
        word_end = gt_detection_level[-1][0]
        self.effective_word_duration = (word_end - word_start)/self.samplerate
        logger.debug('effective_word_duration %f s'%self.effective_word_duration)
        uCTRLR_error = self.effective_word_duration/((N_SYMBOLS -1)*SYMBOL_LENGTH*1e-3)
        logger.debug('uCTRLR_error %f (time ratio)'%uCTRLR_error)
        word_start += start # relative to Decoder extract
        # check if gap is indeed less than TEENSY_MAX_LAG
        silence_length = word_start
        gap = silence_length - symbol_length
        relative_gap = gap/(TEENSY_MAX_LAG*self.samplerate)
        logger.debug('Audio update() gap between sync pulse and word start: ')
        logger.debug('%.2f ms (max value %.2f)'%(1e3*gap/self.samplerate,
                                    1e3*TEENSY_MAX_LAG))
        logger.debug('relative audio_block gap %.2f'%(relative_gap))
        # if relative_gap > 1: # dont tell: simply fail and try elsewhere
        #     print('Warning: gap between spike and word is too big for %s'%self.rec)
        #     print('Audio update() gap between sync pulse and word start: ')
        #     print('%.2f ms (max value %.2f)'%(1e3*gap/self.samplerate,
        #                             1e3*TEENSY_MAX_LAG))
        symbol_width_samples_theor = self.samplerate*SYMBOL_LENGTH*1e-3
        symbol_width_samples_eff = self.effective_word_duration * \
                                            self.samplerate/(N_SYMBOLS - 1)
        logger.debug('symbol width %i theo; %i effective (samples)'%(
                                    symbol_width_samples_theor,
                                    symbol_width_samples_eff))
        symbol_positions = symbol_width_samples_eff * \
            np.arange(float(0), float(N_SYMBOLS - 1)) + word_start
        # symbols_indices contains 34 start of symbols (samples)
        symbols_indices = symbol_positions.round().astype(int)
        if self.do_plots:
            fig, ax = plt.subplots()
            ax.hlines(0, 0, 1,
                transform=ax.get_yaxis_transform(), alpha=0.3,
                linewidth=2, colors='black')
            start = self.sound_extract_position
            i_samples = np.arange(start, start + len(whole_word))
            ax.plot(i_samples, whole_word, marker='o', markersize='1',
                linewidth=1.5,alpha=0.3, color='blue' )
            xt = ax.get_xaxis_transform()
            for x in symbols_indices:
                ax.vlines(x + start, 0, 1,
                    transform=xt,
                linewidth=0.6, colors='green')
                ax.set_title('Slicing the 34 bits word:')
            plt.xlabel("Position in file %s (samples)"%self.rec)
            ax.vlines(start, 0, 1,
                transform=xt,
                linewidth=0.6, colors='red')
            plt.show()
        slice_width = round(SYMBOL_LENGTH*1e-3*self.samplerate)
        slices = [whole_word[i:i+slice_width] for i in symbols_indices]
        return slices

    def _get_main_frequency(self, symbol_data):
        w = np.fft.fft(symbol_data)
        freqs = np.fft.fftfreq(len(w))
        idx = np.argmax(np.abs(w))
        freq = freqs[idx]
        freq_in_hertz = abs(freq * self.samplerate)
        return int(round(freq_in_hertz))


class Recording:
    """
    Wrapper for file objects, ffmpeg read operations and fprobe functions
    
    Attributes:
        AVpath : pathlib.path
            path of video+sound+TicTacCode file, relative to working directory

        audio_data : in16 numpy.array of shape [nchan] x [N samples]

        # valid_sound : pathlib.path
        #     path of sound file stripped of silent and TicTacCode channels

        device : Device
            identifies the device used for the recording, set in __init__()

        probe : dict
            returned value of ffmpeg.probe(self.AVpath)

        TicTacCode_channel : int
            which channel is sync track. 0 is first channel,
            set in _find_TicTacCode().

        decoder : yaltc.decoder
            associated decoder object, if file is audiovideo

        true_samplerate : float
            true sample rate using GPS time

        start_time : datetime or str
            time and date of the first sample in the file, cached
            after a call to get_start_time(). Value on initialization
            is None.

        sync_position : int
            position of first detected syn pulse

        is_audio_reference : bool (True for ref rec only)
            in multi recorders set-ups, user decides if a sound-only recording
            is the time reference for all other audio recordings. By
            default any video recording is the time reference for other audio,
            so this attribute is only relevant to sound recordings and is
            implicitly True for each video recordings (but not set)

        device_relative_speed : float
            the ratio of the recording device clock speed relative to the
            video recorder clock device, in order to correct clock drift with
            pysox tempo transform. If value < 1.0 then the recording is
            slower than video recorder. Updated by each
            MediaMerger instance so the value can change
            depending on the video recording . A mean is calculated for all
            recordings of the same device in
            MediaMerger._get_concatenated_audiofile_for()

        time_position : float
            The time (in seconds) at which the recording starts relative to the
            video recording. Updated by each MediaMerger
            instance so the value can change depending on the video
            recording (a video or main sound).

        final_synced_file : a pathlib.Path
            contains the path of the merged video file after the call to
            AudioStitcher.build_audio_and_write_merged_media if the Recording is a
            video recording, relative to the working directory
            
        synced_audio : pathlib.Path
            contains the path of audio only of self.final_synced_file. Absolute
            path to tempfile.

        in_cam_audio_sync_error : int
            in cam audio sync error, read in the camera folder. Negative value
            for lagging video (audio leads) positive value for lagging audio
            (video leads)


    """

    def __init__(self, media, do_plots=False):
        """
        Set AVfilename string and check if file exists, does not read any
        media data right away but uses ffprobe to parses the file and sets
        probe attribute.

        Logs a warning and sets Recording.decoder to None if ffprobe cant
        interpret the file or if file has no audio. If file contains audio,
        initialise Recording.decoder(but doesnt try to decode anything yet).

        If multifile recording, AVfilename is sox merged audio file;

        Parameters
        ----------
        media : Media dataclass with attributes:
            path: Path
            device: Device

            with Device having attibutes (from device_scanner module):
                UID: int
                folder: Path
                name: str
                dev_type: str
                tracks: Tracks

                with Tracks having attributes (from device_scanner module):
                    ttc: int # track number of TicTacCode signal
                    unused: list # of unused tracks
                    stereomics: list # of stereo mics track tuples (Lchan#, Rchan#)
                    mix: list # of mixed tracks, if a pair, order is L than R
                    others: list #of all other tags: (tag, track#) tuples
                    rawtrx: list # list of strings read from file
                    error_msg: str # 'None' if none
        Raises
        ------
        an Exception if AVfilename doesnt exist

        """
        self.AVpath = media.path
        self.device = media.device
        self.true_samplerate = None
        self.start_time = None
        self.in_cam_audio_sync_arror = 0
        self.decoder = None
        self.probe = None
        self.TicTacCode_channel = None
        self.is_audio_reference = False
        self.device_relative_speed = 1.0
        # self.valid_sound = None
        self.final_synced_file = None
        self.synced_audio = None
        # self.new_rec_name = media.path.name
        self.do_plots = do_plots
        logger.debug('__init__ Recording object %s'%self.__repr__())
        logger.debug(' in directory %s'%self.AVpath.parent)
        recording_init_fail = ''
        if not self.AVpath.is_file():
            raise OSError('file "%s" doesnt exist'%self.AVpath)        
        try:
            self.probe = ffmpeg.probe(self.AVpath)
        except:
            logger.warning('"%s" is not recognized by ffprobe'%self.AVpath)
            recording_init_fail = 'not recognized by ffprobe'
        if self.probe is None:
            recording_init_fail ='no ffprobe'
        elif self.probe['format']['probe_score'] < 99:
            logger.warning('ffprobe score too low')
            # raise Exception('ffprobe_score too low: %i'%probe_score)
            recording_init_fail = 'ffprobe score too low'
        elif not self.has_audio():
            # logger.warning('file has no audio')
            recording_init_fail = 'no audio in file'
        elif self.get_duration() < MINIMUM_LENGTH:
            recording_init_fail = 'file too short, %f s\n'%self.get_duration()
        if recording_init_fail == '': # success
            self.decoder = Decoder(self, do_plots)
            # self._set_multi_files_siblings()
            self._check_for_camera_error_correction()
        else:
            print('For file %s, '%self.AVpath)
            logger.warning('Recording init failed: %s'%recording_init_fail)
            print('Recording init failed: %s'%recording_init_fail)
            self.probe = None
            self.decoder = None
            return
        logger.debug('ffprobe found: %s'%self.probe)
        logger.debug('n audio chan: %i'%self.get_audio_channels_nbr())
        self._read_audio_data()

    def _read_audio_data(self):
        # sets Recording.audio_data
        dryrun = (ffmpeg
            .input(str(self.AVpath))
            .output('pipe:', format='s16le', acodec='pcm_s16le')
            .get_args())
        dryrun = ' '.join(dryrun)
        logger.debug('using ffmpeg-python built args to pipe audio stream into numpy array:\nffmpeg %s'%dryrun)
        try:
            out, _ = (ffmpeg
                # .input(str(path), ss=time_where, t=chunk_length)
                .input(str(self.AVpath))
                .output('pipe:', format='s16le', acodec='pcm_s16le')
                .global_args("-loglevel", "quiet")
                .global_args("-nostats")
                .global_args("-hide_banner")
                .run(capture_stdout=True))
            data = np.frombuffer(out, np.int16)
        except ffmpeg.Error as e:
            print('error',e.stderr)
        n_chan = self.get_audio_channels_nbr()
        if n_chan == 1 and not self.is_video():
            logger.error('file is sound mono')
        if np.isclose(np.std(data), 0, rtol=1e-2):
            logger.error("ffmpeg can't extract audio from %s"%self.AVpath)
        # from 1D  interleaved channels to [chan1, chan2, chanN]
        self.audio_data = data.reshape(int(len(data)/n_chan),n_chan).T
        logger.debug('Recording.audio_data: %s of shape %s'%(self.audio_data,
            self.audio_data.shape))

    def __repr__(self):
        # return 'Recording of %s'%_pathname(self.new_rec_name)
        return _pathname(self.AVpath)

    def _check_for_camera_error_correction(self):
        # look for a file number
        streams = self.probe['streams']
        codecs = [stream['codec_type'] for stream in streams]
        if 'video' in codecs:
            calib_file = list(self.AVpath.parent.rglob('*ms.txt'))
            # print(list(files))
            if len(calib_file) == 1:
                value_string = calib_file[0].stem.split('ms')[0]
                try:
                    value = int(value_string)
                except:
                    f = str(calib_file[0])
                    print('problem parsing name of [gold1]%s[/gold1],'%f)
                    print('move elsewhere and rerun, quitting.\n')
                    sys.exit(1)
                self.in_cam_audio_sync_arror = value
                logger.debug('found error correction %i ms.'%value)

    def get_path(self):
        return self.AVpath

    def get_duration(self):
        """
        Raises
        ------
        Exception
            If ffprobe has no data to compute duration.

        Returns
        -------
        float
            recording duration in seconds.

        """
        if self.is_audio():
            val = sox.file_info.duration(_pathname(self.AVpath))
            logger.debug('sox duration of valid_sound %f for %s'%(val,_pathname(self.AVpath)))
            return val #########################################################
        else:
            if self.probe is None:
                return 0 #######################################################
            try:
                probed_duration = float(self.probe['format']['duration'])
            except:
                logger.error('oups, cant find duration from ffprobe')
                raise Exception('stopping here')
            logger.debug('ffprobed duration is: %f sec for %s'%(probed_duration, self))
            return probed_duration # duration in s

    def get_original_duration(self):
        """
        Raises
        ------
        Exception
            If ffprobe has no data to compute duration.

        Returns
        -------
        float
            recording duration in seconds.

        """
        val = sox.file_info.duration(_pathname(self.AVpath))
        logger.debug('duration of AVpath %f'%val)
        return val

    def get_corrected_duration(self):
        """
        uses device_relative_speed to compute corrected duration. Updated by
        each MediaMerger object in
        MediaMerger._get_concatenated_audiofile_for()
        """
        return self.get_duration()/self.device_relative_speed

    def needs_dedrifting(self):
        rel_sp = self.device_relative_speed
        # if rel_sp > 1:
        #     delta = (rel_sp - 1)*self.get_original_duration()
        # else:
        #     delta = (1 - rel_sp)*self.get_original_duration()
        delta = abs((1 - rel_sp)*self.get_original_duration())
        logger.debug('%s delta drift %.2f ms'%(str(self), delta*1e3))
        if delta > MAXDRIFT:
            print('\n[gold1]%s[/gold1] will get drift correction: delta of [gold1]%.3f[/gold1] ms is too big'%
                (self.AVpath, delta*1e3))
        return delta > MAXDRIFT, delta

    def get_end_time(self):
        return (
            self.get_start_time() + 
            timedelta(seconds=self.get_duration())
            )

        """        
            Check if datetime fits inside recording interval,
            ie if start < datetime < end

            Returns a bool
        
        """
        start = self.get_start_time()
        end = self.get_end_time()
        return start < datetime and datetime < end

    def _find_time_around(self, time):
        """        
        Tries to decode FSK around time (in sec)
        through decoder object; if successful  return a time dict, eg:
        {'version': 0, 'seconds': 44, 'minutes': 57,
        'hours': 19, 'day': 1, 'month': 3, 'year offset': 1, 
        'pulse at': 670451.2217 }
        otherwise return None
        """        
        if time < 0: # negative = referenced from the end
            there = self.get_duration() + time
        else:
            there = time
        self._find_TicTacCode(there, SOUND_EXTRACT_LENGTH)
        if self.TicTacCode_channel is None:
            return None
        else:
            return self.decoder.get_time_in_sound_extract()

    def _get_timedate_from_dict(self, time_dict):
        try:
            python_datetime = datetime(
                time_dict['year offset'] + YEAR_ZERO,
                time_dict['month'],
                time_dict['day'],
                time_dict['hours'],
                time_dict['minutes'],
                time_dict['seconds'],
                tzinfo=timezone.utc)
        except ValueError as e:
            print('Error converting date in _get_timedate_from_dict',e)
            sys.exit(1)
        python_datetime += timedelta(seconds=1) # PPS precedes NMEA sequ
        return python_datetime

    def _two_times_are_coherent(self, t1, t2):
        """
        For error checking. This verifies if two sync pulse apart
        are correctly space with sample interval deduced from
        time difference of demodulated TicTacCode times. The same 
        process is used for determining the true sample rate
        in _compute_true_samplerate(). On entry check if either time
        is None, return False if so.

        Parameters
        ----------
        t1 : dict of demodulated time (near beginning)
            see _find_time_around().
        t2 : dict of demodulated time (near end)
            see _find_time_around().

        Returns
        -------

        """
        if t1 == None or t2 == None:
            return False #######################################################
        logger.debug('t1 : %s t2: %s'%(t1, t2))
        datetime_1 = self._get_timedate_from_dict(t1)
        datetime_2 = self._get_timedate_from_dict(t2)
        # if datetime_2 < datetime_1:
        #     return False
        sample_position_1 = t1['pulse at']
        sample_position_2 = t2['pulse at']
        samplerate = self.get_samplerate()
        delta_seconds_with_samples = \
                (sample_position_2 - sample_position_1)/samplerate
        delta_seconds_with_UTC = (datetime_2 - datetime_1).total_seconds()
        logger.debug('check for delay between \n%s and\n%s'%
                            (datetime_1, datetime_2))
        logger.debug('delay using samples number: %f sec'%
                            (delta_seconds_with_samples))
        logger.debug('delay using timedeltas: %.2f sec'%
                            (delta_seconds_with_UTC))
        if delta_seconds_with_UTC < 0:
            return False
        return round(delta_seconds_with_samples) == delta_seconds_with_UTC

    def _compute_true_samplerate(self, t1, t2):
        datetime_1 = self._get_timedate_from_dict(t1)
        pulse_position_1 = t1['pulse at']
        datetime_2 = self._get_timedate_from_dict(t2)
        if datetime_1 == datetime_2:
            msg = 'times at start and end are indentical, file too short? %s'%self.AVpath
            logger.error(msg)
            raise Exception(msg)
        pulse_position_2 = t2['pulse at']
        delta_seconds_whole = (datetime_2 - datetime_1).total_seconds()
        delta_samples_whole = pulse_position_2 - pulse_position_1
        true_samplerate = delta_samples_whole / delta_seconds_whole
        logger.debug('delta seconds between pulses %f'%
                                delta_seconds_whole)
        logger.debug('delta samples between pulse %i'%
                                delta_samples_whole)
        logger.debug('true sample rate = %s Hz'%
                                to_precision(true_samplerate, 8))
        return true_samplerate

    def set_time_position_to(self, video_clip):
        """
        Sets self.time_position, the time (in seconds) at which the recording
        starts relative to the video recording. Updated by each MediaMerger
        instance so the value can change depending on the video
        recording (a video or main sound).

        called by timeline.AudioStitcher._get_concatenated_audiofile_for()
        
        """
        video_start_time = video_clip.get_start_time()
        self.time_position = (self.get_start_time()
                                            - video_start_time).total_seconds()

    def get_Dt_with(self, later_recording):
        """
        Returns delta time in seconds
        """
        if not later_recording:
            return 0
        t1 = self.get_end_time()
        t2 = later_recording.get_start_time()
        return t2 - t1

    def get_start_time(self):
        """
        Try to decode a TicTacCode_channel at start AND finish;
        if successful, returns a datetime.datetime instance;
        if not returns None.
        """
        logger.debug('for %s, recording.start_time %s'%(self,
                                                        self.start_time))
        if self.decoder is None:
            return None # ffprobe failes or file too short, see __init__
        if self.start_time is not None:
            logger.debug('Recording.start_time already found %s'%self.start_time)
            return self.start_time #############################################
        cached_times = {}
        def find_time(t_sec):
            time_k = int(t_sec)
            # if cached_times.has_key(time_k):
            if CACHING and time_k in cached_times:
                logger.debug('cache hit _find_time_around() for t=%s s'%time_k)
                return cached_times[time_k] ####################################
            else:
                logger.debug('_find_time_around() for t=%s s not cached'%time_k)
                new_t = self._find_time_around(t_sec)
                cached_times[time_k] = new_t
                return new_t
        for i, pair in enumerate(TRIAL_TIMES):
            near_beg, near_end = pair
            logger.debug('Will try to decode times at: %s and %s secs'%
                (near_beg, near_end))
            logger.debug('Trial #%i of %i, beg at %f s'%(i+1,
                                    len(TRIAL_TIMES), near_beg))
            if i > 1:
                logger.warning('More than one trial: #%i/%i'%(i+1,
                                        len(TRIAL_TIMES)))
            # time_around_beginning = self._find_time_around(near_beg)
            time_around_beginning = find_time(near_beg)
            # if self.TicTacCode_channel is None:
            #     return None ####################################################
            logger.debug('Trial #%i, end at %f'%(i+1, near_end))
            # time_around_end = self._find_time_around(near_end)
            time_around_end = find_time(near_end)
            logger.debug('trial result, time_around_beginning:\n   %s'%
                    (time_around_beginning))
            logger.debug('trial result, time_around_end:\n   %s'%
                    (time_around_end))
            coherence = self._two_times_are_coherent(
                    time_around_beginning,
                    time_around_end)
            logger.debug('_two_times_are_coherent: %s'%coherence) 
            if coherence:
                logger.debug('Trial #%i successful'%(i+1))
                break
        if not coherence:
            logger.warning('found times are incoherent')
            return None ########################################################
        if None in [time_around_beginning, time_around_end]:
            logger.warning('didnt find any time in file')
            self.start_time = None
            return None ########################################################
        true_sr = self._compute_true_samplerate(
                        time_around_beginning,
                        time_around_end)
        # self.true_samplerate = to_precision(true_sr,8)
        self.true_samplerate = true_sr
        first_pulse_position = time_around_beginning['pulse at']
        delay_from_start = timedelta(
                seconds=first_pulse_position/true_sr)
        first_time_date = self._get_timedate_from_dict(
                                    time_around_beginning)
        in_cam_correction = timedelta(seconds=self.in_cam_audio_sync_arror/1000)
        start_UTC = first_time_date - delay_from_start + in_cam_correction
        logger.debug('recording started at %s'%start_UTC)
        self.start_time = start_UTC
        self.sync_position = time_around_beginning['pulse at']
        # if self.is_audio():
        #     self.valid_sound = self.AVpath
        return start_UTC

    def _ffprobe_audio_stream(self):
        streams = self.probe['streams']
        audio_streams = [
            stream 
            for stream
            in streams
            if stream['codec_type']=='audio'
            ]
        if len(audio_streams) > 1:
            raise Exception('ffprobe gave multiple audio streams?')
        audio_str = audio_streams[0]
        return audio_str

    def _ffprobe_video_stream(self):
        streams = self.probe['streams']
        audio_streams = [
            stream 
            for stream
            in streams
            if stream['codec_type']=='video'
            ]
        if len(audio_streams) > 1:
            raise Exception('ffprobe gave multiple video streams?')
        audio_str = audio_streams[0]
        return audio_str

    def get_samplerate_drift(self):
        # return drift in ppm (int), relative to nominal sample rate, neg = lag
        nominal = self.get_samplerate()
        true = self.true_samplerate
        if true > nominal:
            ppm = (true/nominal - 1) * 1e6
        else:
            ppm = - (nominal/true - 1) * 1e6
        return int(ppm)

    def get_speed_ratio(self, videoclip):
        # ratio between real samplerates of audio and videoclip
        nominal = self.get_samplerate()
        true = self.true_samplerate
        ratio = true/nominal
        nominal_vid = videoclip.get_samplerate()
        true_ref = videoclip.true_samplerate
        ratio_ref = true_ref/nominal_vid
        return ratio/ratio_ref

    def get_samplerate(self):
        # returns int samplerate (nominal)
        string = self._ffprobe_audio_stream()['sample_rate']
        logger.debug('ffprobe samplerate: %s'%string)
        return eval(string)

    def get_framerate(self):
        string = self._ffprobe_video_stream()['avg_frame_rate']
        return eval(string) # eg eval(24000/1001)

    def get_start_timecode_string(self, with_offset=0):
        # returns a HH:MM:SS:FR string
        start_datetime = self.get_start_time()
        # logger.debug('CLI_offset %s'%CLI_offset)
        logger.debug('start_datetime %s'%start_datetime)
        start_datetime += timedelta(seconds=with_offset)
        logger.debug('shifted start_datetime %s (offset %f)'%(start_datetime,
                                                    with_offset))
        HHMMSS = start_datetime.strftime("%H:%M:%S")
        fps = self.get_framerate()
        frame_number = str(round(fps*1e-6*start_datetime.microsecond))
        timecode  = HHMMSS + ':' + frame_number.zfill(2)
        logger.debug('timecode: %s'%(timecode))
        return timecode

    def write_file_timecode(self, timecode):
        # set self.final_synced_file metadata to timecode string
        if self.final_synced_file == None:
            logger.error('cant write timecode for unexisting file, quitting..')
            raise Exception
        try:
            video_path = self.final_synced_file
            in1 = ffmpeg.input(_pathname(video_path))
            video_extension = video_path.suffix
            silenced_opts = ["-loglevel", "quiet", "-nostats", "-hide_banner"]
            file_handle = tempfile.NamedTemporaryFile(suffix=video_extension, delete=DEL_TEMP)
            out1 = in1.output(file_handle.name,
                timecode=timecode,
                acodec='copy', vcodec='copy')
            ffmpeg.run([out1.global_args(*silenced_opts)], overwrite_output=True)
        except ffmpeg.Error as e:
            logger.error('ffmpeg.run error')
            logger.error(e)
            logger.error(e.stderr)
        os.remove(_pathname(video_path))
        shutil.copy(_pathname(file_handle), _pathname(video_path))

    def has_audio(self):
        if not self.probe:
            return False #######################################################
        streams = self.probe['streams']
        codecs = [stream['codec_type'] for stream in streams]
        return 'audio' in codecs

    def get_audio_channels_nbr(self):
        if not self.has_audio():
            return 0 ###########################################################
        audio_str = self._ffprobe_audio_stream()
        return audio_str['channels']

    def is_video(self):
        if not self.probe:
            return False #######################################################
        streams = self.probe['streams']
        codecs = [stream['codec_type'] for stream in streams]
        return 'video' in codecs

    def is_audio(self):
        return not self.is_video()

    def _find_TicTacCode(self, time_where, chunk_length):
        """
        Extracts a chunk from Recording.audio_data and sends it to
        Recording.decoder object with set_sound_extract_and_sr() to find which
        channel contains a TicTacCode track and sets TicTacCode_channel
        accordingly (index of channel). On exit, self.decoder.sound_extract
        contains TicTacCode data ready to be demodulated. If not,
        self.TicTacCode_channel is set to None.

        If this has been called before (checking self.TicTacCode_channel) then
        is simply read the audio in and calls set_sound_extract_and_sr(). 

        Args:
            time_where : float
                time of the audio chunk start, in seconds.
            chunk_length : float
                length of the audio chunk, in seconds.

        Calls:
            self.decoder.set_sound_extract_and_sr()

        Sets:
            self.TicTacCode_channel = index of TTC chan
            self.device.ttc  = index of TTC chan

        Returns:
            this Recording instance

        """
        path = self.AVpath
        decoder = self.decoder
        if decoder:
            decoder.clear_decoder()
        if not self.has_audio():
            self.TicTacCode_channel = None
            return #############################################################
        sound_data_var = np.std(self.audio_data)
        sound_extract_position = int(self.get_samplerate()*time_where)
        logger.debug('extracting sound at %i with variance %f'%(
                                                    sound_extract_position,
                                                    sound_data_var))
        if self.TicTacCode_channel == None:
            logger.debug('first call, will loop through all %i channels'%len(
                                        self.audio_data))
            for i_chan, chan_dat in enumerate(self.audio_data):
                logger.debug('testing chan %i'%i_chan)
                start_idx = round(time_where*self.get_samplerate())
                extract_length = round(chunk_length*self.get_samplerate())
                end_idx = start_idx + extract_length
                extract_audio_data = chan_dat[start_idx:end_idx]
                decoder.set_sound_extract_and_sr(
                        extract_audio_data,
                        self.get_samplerate(),
                        sound_extract_position
                        )
                if decoder.extract_seems_TicTacCode():
                    self.TicTacCode_channel = i_chan
                    self.device.ttc = i_chan
                    logger.debug('found TicTacCode channel: chan #%i'%
                                    self.TicTacCode_channel)
                    return self ################################################
            # end of loop: none found
            # self.TicTacCode_channel = None # was None already 
            logger.warning('found no TicTacCode channel')
        else:
            logger.debug('been here before, TTC chan is %i'%
                                                self.TicTacCode_channel)
            start_idx = round(time_where*self.get_samplerate())
            extract_length = round(chunk_length*self.get_samplerate())
            end_idx = start_idx + extract_length
            chan_dat = self.audio_data[self.TicTacCode_channel]
            extract_audio_data = chan_dat[start_idx:end_idx]
            decoder.set_sound_extract_and_sr(
                    extract_audio_data,
                    self.get_samplerate(),
                    sound_extract_position
                    )
        return self
    
    def does_overlap_with_time(self, time):
        A1, A2 = self.get_start_time(), self.get_end_time()
        # R1, R2 = rec.get_start_time(), rec.get_end_time()
        # no_overlap = (A2 < R1) or (A1 > R2)
        return time >= A1 and time <= A2

    def get_otio_videoclip(self):
        if self.new_rec_name == self.AVpath.name:
            # __init__ value still the same?
            logger.error('cant get otio clip if no editing has been done.')
            raise Exception
        clip = otio.schema.Clip()
        clip.name = self.new_rec_name.stem
        clip.media_reference = otio.schema.ExternalReference(
            target_url=_pathname(Path.cwd()/self.final_synced_file))
        length_in_ms = self.get_duration()*1e3 # for RationalTime later
        clip.source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 1), 
            duration=otio.opentime.RationalTime(int(length_in_ms), 1000)
            )
        return clip

    def get_otio_audioclip(self):
        # and place a copy of audio in tictacsync directory
        if not self.synced_audio:
            # no synced audio
            logger.error('cant get otio clip if no editing has been done.')
            raise Exception
        video = self.final_synced_file
        path_WO_suffix = _pathname(Path.cwd()/video).split('.')[0] #better way?
        audio_destination = path_WO_suffix + '.wav'
        shutil.copy(self.synced_audio, audio_destination)
        logger.debug('copied %s'%audio_destination)
        clip = otio.schema.Clip()
        clip.name = self.new_rec_name.stem + ' audio'
        clip.media_reference = otio.schema.ExternalReference(
            target_url=audio_destination)
        length_in_ms = self.get_duration()*1e3 # for RationalTime later
        clip.source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 1), 
            duration=otio.opentime.RationalTime(int(length_in_ms), 1000)
            )
        return clip

