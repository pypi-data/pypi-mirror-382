# -*- coding: utf-8 -*-
import numpy, tempfile, copy
# import ffmpeg, pathlib, os
import ffmpeg
from loguru import logger
import sox
from pathlib import Path
from rich import print
from itertools import groupby
# import opentimelineio as otio
from datetime import timedelta
import shutil, os, sys, stat, subprocess
from subprocess import Popen, PIPE
from pprint import pformat

from inspect import currentframe, getframeinfo
try:
    from . import yaltc
    from . import device_scanner
except:
    import yaltc
    import device_scanner

CLUSTER_GAP = 2 # secs between multicam clusters
DEL_TEMP = False
DB_OSX_NORM = -6 #dB
OUT_DIR_DEFAULT = 'SyncedMedia'
MCCDIR = 'SyncedMulticamClips'


# utility to lock ISO audio files
def remove_write_permissions(path):
    """Remove write permissions from this path, while keeping all other permissions intact.

    Params:
        path:  The path whose permissions to alter.
    """
    NO_USER_WRITING = ~stat.S_IWUSR
    NO_GROUP_WRITING = ~stat.S_IWGRP
    NO_OTHER_WRITING = ~stat.S_IWOTH
    NO_WRITING = NO_USER_WRITING & NO_GROUP_WRITING & NO_OTHER_WRITING
    current_permissions = stat.S_IMODE(os.lstat(path).st_mode)
    os.chmod(path, current_permissions & NO_WRITING)

# utility for accessing pathnames
def _pathname(tempfile_or_path) -> str:
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path ################################################
    if isinstance(tempfile_or_path, yaltc.Recording):
        return str(tempfile_or_path.AVpath) ####################################
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path) ###########################################
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name ###########################################
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

# utility for printing groupby results
def print_grby(grby):
    for key, keylist in grby:
        print('\ngrouped by %s:'%key)
        for e in keylist:
            print(' ', e)

# deltatime utility
def from_midnight(a_datetime) -> timedelta:
    # returns a deltatime from a datetime, "dropping" the date information
    return(timedelta(hours=a_datetime.hour, minutes=a_datetime.minute,
                     seconds=a_datetime.second,
                     microseconds=a_datetime.microsecond))

# utility for extracting one audio channel
def _extr_channel(source, dest, channel):
    # int channel = 1 for first channel
    # returns nothing, output is written to the filesystem
    sox_transform = sox.Transformer()
    mix_dict = {1:[channel]}
    logger.debug('sox args %s %s %s'%(source, dest, mix_dict))    
    sox_transform.remix(mix_dict)
    logger.debug('sox transform %s'%str(sox_transform))
    status = sox_transform.build(str(source), str(dest))
    logger.debug('sox status %s'%status)

def _same(aList):
    return aList.count(aList[0]) == len(aList)

def _flatten(xss):
    return [x for xs in xss for x in xs]

def _sox_keep(audio_file, kept_channels: list) -> tempfile.NamedTemporaryFile:
    """
    Returns a NamedTemporaryFile containing the selected kept_channels

    Channels numbers in kept_channels are not ZBIDXed as per SOX format
    """
    audio_file = _pathname(audio_file)
    nchan = sox.file_info.channels(audio_file)
    logger.debug('in file of %i chan, have to keep %s'%
        (nchan, kept_channels))
    all_channels = range(1, nchan + 1) # from 1 to nchan included
    # Building dict according to pysox.remix format.
    # https://pysox.readthedocs.io/en/latest/api.html#sox.transform.Transformer.remix
    # eg:   {1: [3], 2: [4]} to keep channels 3 & 4    
    kept_channels = [[n] for n in kept_channels]
    sox_remix_dict = dict(zip(all_channels, kept_channels))
    output_tempfile = tempfile.NamedTemporaryFile(suffix='.wav', delete=DEL_TEMP)
    out_file = _pathname(output_tempfile)
    logger.debug('sox in and out files: %s %s'%(audio_file, out_file))
    # sox_transform.set_output_format(channels=1)
    sox_transform = sox.Transformer()
    sox_transform.remix(sox_remix_dict)
    logger.debug('sox remix transform: %s'%sox_transform)
    logger.debug('sox remix dict: %s'%sox_remix_dict)
    status = sox_transform.build(audio_file, out_file, return_output=True )
    logger.debug('sox.build exit code %s'%str(status))
    p = Popen('ffprobe %s -hide_banner'%audio_file,
        shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    logger.debug('remixed input_file ffprobe:\n%s'%(stdout +
        stderr).decode('utf-8'))
    p = Popen('ffprobe %s -hide_banner'%out_file,
        shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    logger.debug('remixed out_file ffprobe:\n%s'%(stdout +
        stderr).decode('utf-8'))
    return output_tempfile

def _sox_split_channels(multi_chan_audio:Path) -> list:
    nchan = sox.file_info.channels(_pathname(multi_chan_audio))
    source = _pathname(multi_chan_audio)
    paths = []
    for i in range(nchan):
        out_fh = tempfile.NamedTemporaryFile(suffix='.wav',
                delete=DEL_TEMP)
        sox_transform = sox.Transformer()
        mix_dict = {1:[i+1]}
        sox_transform.remix(mix_dict)
        dest = _pathname(out_fh)
        status = sox_transform.build(source, dest)
        logger.debug('source %s dest %s'%(source, dest))
        logger.debug('sox status %s'%status)
        paths.append(out_fh)
    logger.debug('paths %s'%paths)
    return paths

def _sox_combine(paths) -> Path:
    """
    Combines (stacks) files referred by the list of Path into a new temporary
    files passed on return each files are stacked in a different channel, so
    len(paths) == n_channels
    """
    if len(paths) == 1: # one device only, nothing to stack
        logger.debug('one device only, nothing to stack')
        return paths[0] ########################################################
    out_file_handle = tempfile.NamedTemporaryFile(suffix='.wav',
        delete=DEL_TEMP)
    filenames = [_pathname(p) for p in paths]
    out_file_name = _pathname(out_file_handle)
    logger.debug('combining files: %s into %s'%(
        filenames,
        out_file_name))
    cbn = sox.Combiner()
    cbn.set_input_format(file_type=['wav']*len(paths))
    status = cbn.build(
        filenames,
        out_file_name,
        combine_type='merge')
    logger.debug('sox.build status: %s'%status)
    if status != True:
        print('Error, sox did not merge files in _sox_combine()')
        sys.exit(1)
    merged_duration = sox.file_info.duration(
        _pathname(out_file_handle))
    nchan = sox.file_info.channels(
        _pathname(out_file_handle)) 
    logger.debug('merged file duration %f s with %i channels '%
        (merged_duration, nchan))
    return out_file_handle

def _sox_multi2stereo(multichan_tmpfl, stereo_trxs) -> tempfile.NamedTemporaryFile:

    """
    This mixes down all the tracks in multichan_tmpfl to a stereo wav file. Any
    mono tracks are panned 50-50 (mono tracks are those not present in argument
    stereo_trxs)

    Args:
        multichan_tmpfl : tempfile.NamedTemporaryFile
            contains the edited and synced audio, almost ready to be merged
            with the concurrent video file
        stereo_trxs : list of pairs of integers
            each pairs identifies a left-right tracks, 1st track in
            multichan_tmpfl is index 1 (sox is not ZBIDX)
    Returns:
        the tempfile.NamedTemporaryFile of a stereo wav file
        containing the audio to be merged with the video
    """
    n_chan_input = sox.file_info.channels(_pathname(multichan_tmpfl))
    logger.debug('n chan input: %s'%n_chan_input)
    if n_chan_input == 1: # nothing to mix down
        return multichan_tmpfl #################################################
    stereo_tempfile = tempfile.NamedTemporaryFile(suffix='.wav',
                    delete=DEL_TEMP)
    tfm = sox.Transformer()
    tfm.channels(1) # why ? https://pysox.readthedocs.io/en/latest/api.html?highlight=channels#sox.transform.Transformer.channels
    status = tfm.build(_pathname(multichan_tmpfl),_pathname(stereo_tempfile))
    logger.debug('n chan ouput: %s'%
                sox.file_info.channels(_pathname(stereo_tempfile)))
    logger.debug('sox.build status for _sox_multi2stereo(): %s'%status)
    if status != True:
        print('Error, sox did not normalize file in _sox_multi2stereo()')
        sys.exit(1)
    return stereo_tempfile

def _sox_mix_channels(multichan_tmpfl, stereo_pairs=[]) -> tempfile.NamedTemporaryFile:
    """
    Returns a mix down of the multichannel wav file. If stereo_pairs list is
    empty, a mono mix is done with all the channel present in multichan_tmpfl.
    If stereo_pairs contains one or more elements, a stereo mix is returned with
    the specified Left-Right pairs and all other mono tracks (panned 50-50)

    Note: stereo_pairs numbers are not ZBIDXed
    """
    n_chan_input = sox.file_info.channels(_pathname(multichan_tmpfl))
    logger.debug('n chan input: %s'%n_chan_input)
    if n_chan_input == 1: # nothing to mix down
        return multichan_tmpfl #################################################
    if stereo_pairs == []:
        # all mono
        mono_tpfl = tempfile.NamedTemporaryFile(suffix='.wav',
                        delete=DEL_TEMP)
        tfm = sox.Transformer()
        tfm.channels(1)
        status = tfm.build(_pathname(multichan_tmpfl),_pathname(mono_tpfl))
        logger.debug('number of chan in ouput: %s'%
                    sox.file_info.channels(_pathname(mono_tpfl)))
        logger.debug('sox.build status for _sox_mix_channels(): %s'%status)
        if status != True:
            print('Error, sox did not normalize file in _sox_mix_channels()')
            sys.exit(1)
        return mono_tpfl
    else:
        # stereo tracks present, so stereo output
        logger.debug('stereo tracks present %s, so stereo output'%stereo_pairs)
        stereo_files = [_sox_keep(pair) for pair in stereo_pairs]
    return 

def _sox_mono2stereo(temp_file) -> tempfile.NamedTemporaryFile:
    # upgrade a mono file to stereo panning 50-50
    stereo_tempfile = tempfile.NamedTemporaryFile(suffix='.wav',
                    delete=DEL_TEMP)
    tfm = sox.Transformer()
    tfm.channels(2)
    status = tfm.build(_pathname(temp_file),_pathname(stereo_tempfile))
    logger.debug('n chan ouput: %s'%
                sox.file_info.channels(_pathname(stereo_tempfile)))
    logger.debug('sox.build status for _sox_mono2stereo(): %s'%status)
    if status != True:
        print('Error, sox did not normalize file in _sox_mono2stereo()')
        sys.exit(1)
    return stereo_tempfile

def _sox_mix_files(temp_files_to_mix:list) -> tempfile.NamedTemporaryFile:
    """
    Mix files referred by the list of Path into a new temporary files passed on
    return. If one of the files is stereo, upgrade each mono file to a panned
    50-50 stereo file before mixing.
    """
    def _sox_norm(tempf):
        normed_tempfile = tempfile.NamedTemporaryFile(suffix='.wav',
                        delete=DEL_TEMP)
        tfm = sox.Transformer()
        tfm.norm(DB_OSX_NORM)
        status = tfm.build(_pathname(tempf),_pathname(normed_tempfile))
        logger.debug('sox.build status for norm(): %s'%status)
        if status != True:
            print('Error, sox did not normalize file in _sox_mix_files()')
            sys.exit(1)
        return normed_tempfile
    N = len(temp_files_to_mix)
    if N == 1: # nothing to mix
        logger.debug('one file: nothing to mix')
        return temp_files_to_mix[0] ########################################################
    cbn = sox.Combiner()
    cbn.set_input_format(file_type=['wav']*N)
    # check if stereo files are present
    max_n_chan = max([sox.file_info.channels(f) for f
                                in [_pathname(p) for p in temp_files_to_mix]])
    logger.debug('max_n_chan %s'%max_n_chan)
    if max_n_chan == 2:
        # upgrade all mono to stereo
        stereo_tempfiles = [p for p in temp_files_to_mix
            if sox.file_info.channels(_pathname(p)) == 2 ]
        mono_tempfiles = [p for p in temp_files_to_mix
            if sox.file_info.channels(_pathname(p)) == 1 ]
        logger.debug('there are %i mono files and %i stereo files'%
            (len(stereo_tempfiles), len(mono_tempfiles)))
        new_stereo = [_sox_mono2stereo(tmpfl) for tmpfl
                            in mono_tempfiles]
        stereo_tempfiles += new_stereo
        files_to_mix = [_pathname(tempfl) for tempfl in stereo_tempfiles]
    else:
        # all mono
        files_to_mix = [_pathname(tempfl) for tempfl in temp_files_to_mix]
    mixed_tempf = tempfile.NamedTemporaryFile(suffix='.wav',delete=DEL_TEMP)
    status = cbn.build(files_to_mix,
                _pathname(mixed_tempf),
                combine_type='mix',
                input_volumes=[1/N]*N)
    logger.debug('sox.build status for mix: %s'%status)
    if status != True:
        print('Error, sox did not mix files in _sox_mix_files()')
        sys.exit(1)
    normed_tempfile = tempfile.NamedTemporaryFile(suffix='.wav',delete=DEL_TEMP)
    tfm = sox.Transformer()
    tfm.norm(DB_OSX_NORM)
    status = tfm.build(_pathname(mixed_tempf),_pathname(normed_tempfile))
    logger.debug('sox.build status for norm(): %s'%status)
    if status != True:
        print('Error, sox did not normalize file in _sox_mix_files()')
        sys.exit(1)
    return normed_tempfile

class AudioStitcherVideoMerger:
    """
    Typically each found video is associated with an AudioStitcherVideoMerger
    instance. AudioStitcherVideoMerger does the actual audio-video file
    processing of merging AudioStitcherVideoMerger.videoclip (gen. a video)
    with all audio files in  AudioStitcherVideoMerger.soxed_audio as
    determined by the Matcher object (Matcher instanciates and manages
    AudioStitcherVideoMerger objects).

    All audio file edits are done using pysox and video+audio merging with
    ffmpeg. When necessary, clock drift is corrected for all overlapping audio
    devices to match the precise clock value of the ref recording (to a few
    ppm), using sox tempo transform.

    N.B.: A audio_stitch doesn't extend beyond the corresponding videoclip
    video start and end times: it is not a audio montage for the whole movie
    project.


    Class attribute

        tempoed_recs : dict as {Recording : path}

            a cache for already time-stretched audio files. Keys are elements
            of matched_audio_recordings and the value are tuples:
            (factor, file_handle), the file_handle points to the precedently
            produced NamedTemporaryFile; factor is the value that was used in
            the sox tempo transform.

    Attributes:

        videoclip : a Recording instance
            The video to which audio files are synced

        ref_audio : a Recording instance
            If no video is present, this is the reference audio to which others
            audio files are synced

        soxed_audio : dict as {Recording : path}
            keys are elements of matched_audio_recordings and the value are
            the Pathlib path of the eventual edited audio(trimmed or padded).

        synced_clip_dir : Path
            where synced clips are written

    """
    tempoed_recs = {}

    def __init__(self, video_clip):
        self.videoclip = video_clip
        # self.matched_audio_recordings = []
        self.soxed_audio = {}
        logger.debug('instantiating AudioStitcherVideoMerger for %s'%
                            video_clip)

    def add_matched_audio(self, audio_rec):
        """
        Populates AudioStitcherVideoMerger.soxed_audio,
        a dict as {Recording : path}

        This fct is called
        within Matcher.scan_audio_for_each_videoclip()

        Returns nothing, fills self.soxed_audio dict with
        matched audio.

        """
        self.soxed_audio[audio_rec] = audio_rec.AVpath
        """
        Here at this point, self.soxed_audio[audio_rec] is unedited but
        after a call to _edit_audio_file(), soxed_audio[audio_rec] points to
        a new file and audio_rec.AVpath is unchanged.
        """
        return

    def get_matched_audio_recs(self):
        """
        Returns audio recordings that overlap self.videoclip.
        Simply keys of self.soxed_audio dict
        """
        logger.debug(f'soxed_audio {pformat(self.soxed_audio)}')
        return list(self.soxed_audio.keys())

    def _get_audio_devices(self):
        devices = set([r.device for r in self.get_matched_audio_recs()])
        logger.debug('get_matched_audio_recs: %s'%
            pformat(self.get_matched_audio_recs()))
        logger.debug('devices %s'%devices)
        return devices

    def _get_secondary_audio_devices(self):
        # when only audio devices are synced.
        # identical to _get_audio_devices()...
        # name changed for clarity
        return self._get_audio_devices()

    def _get_all_recordings_for(self, device):
        # return recordings for a particular device, sorted by time
        recs = self.get_matched_audio_recs()
        logger.debug(f'device: {device.name} matched audio recs: {recs}')
        recs = [a for a in recs if a.device == device]
        recs.sort(key=lambda r: r.start_time)
        return recs

    def _dedrift_rec(self, rec):
        # instanciates a sox.Transformer() with tempo() effect
        # add applies it via a call to _edit_audio_file(rec, sox_transform)
        tempo_scale_factor = rec.device_relative_speed
        audio_dev = rec.device.name
        video_dev = self.videoclip.device.name
        print('when merging with [gold1]%s[/gold1].'%self.videoclip)
        if tempo_scale_factor > 1:
            print('Because [gold1]%s[/gold1] clock too fast relative to [gold1]%s[/gold1]: file is too long by a %.12f factor;'%
                (audio_dev, video_dev, tempo_scale_factor))
        else:
            print('Because [gold1]%s[/gold1] clock too slow relative to [gold1]%s[/gold1]: file is short by a %.12f factor'%
                (audio_dev, video_dev, tempo_scale_factor))
        logger.debug('tempoed_recs dict:%s'%AudioStitcherVideoMerger.tempoed_recs)
        if rec in AudioStitcherVideoMerger.tempoed_recs:
            logger.debug('%s already tempoed'%rec)
            cached_factor, cached_file = AudioStitcherVideoMerger.tempoed_recs[rec]
            error_factor = tempo_scale_factor/cached_factor
            logger.debug('tempo factors, needed: %f cached %f'%(tempo_scale_factor,cached_factor))
            delta_cache = abs((1 - error_factor)*rec.get_original_duration())
            logger.debug('error if cache is used: %f ms'%(delta_cache*1e3))
            delta_cache_is_ok = delta_cache < yaltc.MAXDRIFT
        else:
            delta_cache_is_ok = False
        if delta_cache_is_ok:
            logger.debug('ok, will use %s'%cached_file)
            self.soxed_audio[rec] = cached_file
        else:
            logger.debug('%s not tempoed yet'%rec)            
            sox_transform = sox.Transformer()
            sox_transform.tempo(tempo_scale_factor)
            # scaled_file = self._get_soxed_file(rec, sox_transform)
            logger.debug('sox_transform %s'%sox_transform.effects)
            soxed_fh = self._edit_audio_file(rec, sox_transform)
            scaled_file_name = _pathname(soxed_fh)
            AudioStitcherVideoMerger.tempoed_recs[rec] = (tempo_scale_factor, soxed_fh)
            new_duration = sox.file_info.duration(scaled_file_name)
            initial_duration = sox.file_info.duration(
                _pathname(rec.AVpath))
            logger.debug('Verif: initial_duration %.12f new_duration %.12f ratio:%.12f'%(
                initial_duration, new_duration, initial_duration/new_duration))
            logger.debug('delta duration %f ms'%((new_duration-initial_duration)*1e3))

    def _get_concatenated_audiofile_for(self, device):
        """
        return a handle for the final audio file formed by all detected
        overlapping recordings, produced by the same audio recorder.
        
        """
        logger.debug('concatenating device %s'%str(device))
        audio_recs = self._get_all_recordings_for(device)
        # [TODO here] Check if all unidentified device files are not
        # overlapping because they are considered produced by the same
        # device. If some overlap then necessarily they're from different
        # ones. List the files and warn the user there is a risk of error if
        # they're not from the same device.

        logger.debug('%i audio files for videoclip %s:'%(len(audio_recs),
            self.videoclip))
        for r in audio_recs:
            logger.debug('  %s'%r)
        # ratio between real samplerates of audio and videoclip
        speeds = numpy.array([rec.get_speed_ratio(self.videoclip)
                                    for rec in audio_recs])
        mean_speed = numpy.mean(speeds)
        for audio in audio_recs:
            audio.device_relative_speed = mean_speed
            logger.debug('set device_relative_speed for %s'%audio)
            logger.debug(' value: %f'%audio.device_relative_speed)
            audio.set_time_position_to(self.videoclip)
            logger.debug('time_position for %s: %fs relative to %s'%(audio,
                audio.time_position, self.videoclip))
        # st_dev_speeds just to check for anomalous situation
        st_dev_speeds = numpy.std(speeds)
        logger.debug('mean speed for %s: %.6f std dev: %.0e'%(device,
                                                    mean_speed,
                                                    st_dev_speeds))
        if st_dev_speeds > 1.0e-5:
            logger.error('too much variation for device speeds')
            sys.exit(1)
        """        
        Because of length
        transformations with pysox.tempo, it is not the sum of REC durations
        
                ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ref
                  ┏━━━━┓   ┏━━━━┓
                ┣━┻━━━━┻━━━┻━━━━┛ growing_file
        
                ├───────────────┤
                             end_time
        
        """

        # process first element 'by hand' outside the loop
        # first_audio is a Recording, not a path nor filehandle
        first_audio = audio_recs[0]
        needs_dedrift, delta = first_audio.needs_dedrifting()
        logger.debug('first audio is %s'%first_audio)
        logger.debug('checking drift, first audio: delta of %0.2f ms'%(
            delta*1e3))
        if needs_dedrift:
            self._dedrift_rec(first_audio)
        else:
            logger.debug('no time stretch for 1st audio')        
        self._pad_or_trim_first_audio(first_audio)
        # loop for the other files
        # growing_file = first_audio.edited_version
        growing_file = self.soxed_audio[first_audio]
        for i, rec in enumerate(audio_recs[1:]):
            logger.debug('Padding and joining for %s'%rec)
            needs_dedrift, delta = rec.needs_dedrifting()
            logger.debug('next audio is %s'%rec)
            logger.debug('checking drift for next audio, delta of %0.2f ms'%(
                delta*1e3))
            if needs_dedrift:
                # logger.debug('dedrifting too...delta of %0.2f ms'%(delta*1e3))
                self._dedrift_rec(rec)
            else:
                logger.debug('no dedrifting')        
            end_time = sox.file_info.duration(growing_file.name)
            logger.debug('  growing_file %s'%(growing_file.name))
            logger.debug('  growing_file duration %.2f'%(end_time))
            logger.debug('  rec.time_position  for next audio %s %.2f'%(rec,
                rec.time_position))
            # TODO check if rec.needs_dedrifting() before padding
            pad_duration = rec.time_position - end_time
            if pad_duration < 0:
                raise Exception('for rec %s, time_position < end_time? %f %f'%
                    (rec,rec.time_position,end_time))
            self._pad_file(rec, pad_duration)
            # new_file = rec.edited_version
            new_file = self.soxed_audio[rec]
            growing_file = self._concatenate_audio_files(growing_file, new_file)
        end_time = sox.file_info.duration(growing_file.name)
        logger.debug('total edited audio duration  %.2f s'%end_time)
        logger.debug('video duration  %.2f s'%
            self.videoclip.get_duration())
        return growing_file

    def _pad_or_trim_first_audio(self, first_rec):
        """
        TODO: check if first_rec is a Recording or tempfile (maybe a tempfile if dedrifted)
        NO: will change tempo after trimming/padding

        Store (into Recording.soxed_audio dict) the handle  of the sox processed
        first recording, padded or chopped according to AudioStitcherVideoMerger.videoclip
        starting time. Length of the written file can differ from length of the
        submitted Recording object if drift is corrected with sox tempo
        transform, so check it with sox.file_info.duration()
        """
        logger.debug(' editing %s'%first_rec)
        audio_start  = first_rec.get_start_time()
        video_start = self.videoclip.get_start_time()
        if video_start < audio_start: # padding
            logger.debug('padding')
            pad_duration  = (audio_start-video_start).total_seconds()
            """padding first_file:
                    ┏━━━━━━━━━━━━━━━┓
                    ┗━━━━━━━━━━━━━━━┛ref
                      ┏━━━━━━┓
                    ┣━┻━━━━━━┛
            """
            self._pad_file(first_rec, pad_duration)
        else:
            logger.debug('trimming')
            length = (video_start-audio_start).total_seconds()
            """chopping first_file:
                    ┏━━━━━━━━━━━━━━━┓
                    ┗━━━━━━━━━━━━━━━┛ref
                  ┏━╋━━━━┓
                  ┗━┻━━━━┛
            """
            self._chop_file(first_rec, length)
        return

    def _concatenate_audio_files(self, f1, f2):
        # return a tmp file object resulting in f1 f2 concatenation
        # on exit f1 and f2 are closed()
        cbn = sox.Combiner()
        out_file = tempfile.NamedTemporaryFile(suffix='.wav',  delete=DEL_TEMP)
        out_file_name = out_file.name
        status = cbn.build(
            [f1.name, f2.name],
            out_file_name,
            combine_type='concatenate',
            )
        logger.debug('sox.build exit code %s'%str(status))
        f1.close()
        f2.close()
        return out_file

    def _pad_file(self, recording, pad_duration):
        # set recording.edited_version to the handle file a sox padded audio
        logger.debug('sox_transform.pad arg: %f secs'%pad_duration)
        sox_transform = sox.Transformer()
        sox_transform.pad(pad_duration)
        self._edit_audio_file(recording, sox_transform)

    def _chop_file(self, recording, length):
        # set recording.edited_version to the handle file a sox chopped audio
        sox_transform = sox.Transformer()
        sox_transform.trim(length)
        logger.debug('sox_transform.trim arg: %f secs'%length)
        self._edit_audio_file(recording, sox_transform)

    def _edit_audio_file(self, audio_rec, sox_transform):
        """
        Apply the specified sox_transform onto the audio_rec and update
        self.soxed_audio dict with the result (with audio_rec as the key)
        Returns the filehandle of the result.
        """
        output_fh = tempfile.NamedTemporaryFile(suffix='.wav', delete=DEL_TEMP)
        logger.debug('transform: %s'%sox_transform.effects)
        recording_fh = self.soxed_audio[audio_rec]
        logger.debug('for recording %s, matching %s'%(audio_rec,
                                                self.videoclip))
        input_file = _pathname(recording_fh)
        logger.debug('AudioStitcherVideoMerger.soxed_audio[audio_rec]: %s'%
                                                    input_file)
        out_file = _pathname(output_fh)
        logger.debug('sox in and out files: %s %s'%(input_file, out_file))
        logger.debug('calling sox_transform.build()')
        status = sox_transform.build(input_file, out_file, return_output=True )
        logger.debug('sox.build exit code %s'%str(status))
        # audio_rec.edited_version = output_fh
        self.soxed_audio[audio_rec] = output_fh
        return output_fh

    def _write_ISOs(self, edited_audio_all_devices,
                snd_root=None, synced_root=None, raw_root=None, audio_only=False):
        """
        [TODO: this multiline doc is obsolete]
        Writes isolated audio files that were synced to synced_clip_file,
        each track will have its dedicated monofile, named sequentially or with
        the name find in TRACKSFILE if any, see Scanner._get_tracks_from_file()

        edited_audio_all_devices:
            a list of (name, mono_tempfile, dev) -------------------------------------------> add argument for device for calling _get_all_recordings_for() for file for metada

        Returns nothing, output is written to filesystem as below.
        ISOs subfolders structure when user invokes the --isos flag:

        SyncedMedia/ (or anchor_dir)

                leftCAM/

                    canon24fps01.MOV ━━━━┓ name of clip is name of folder
                    canon24fps01_ISO/ <━━┛
                        chan_1.wav     
                        chan_2.wav     [UPDATE FOR MAM mode]
                    canon24fps02.MOV 
                    canon24fps01_ISO/ 
                        chan_1.wav
                        chan_2.wav

                rightCAM/
        """
        def _fit_length(audio_tempfile) -> tempfile.NamedTemporaryFile:
            """            
            Changes the length of audio contained in audio_tempfile so it is the
            same as video length associated with this AudioStitcherVideoMerger.
            Returns a tempfile.NamedTemporaryFile with the new audio
            """         
            sox_transform = sox.Transformer()
            audio_length = sox.file_info.duration(_pathname(audio_tempfile))
            video_length = self.videoclip.get_duration()
            if audio_length > video_length:
                # trim audio
                sox_transform.trim(0, video_length)
            else:
                # pad audio
                sox_transform.pad(0, video_length - audio_length)
            out_tf = tempfile.NamedTemporaryFile(suffix='.wav',
                                                    delete=DEL_TEMP)
            logger.debug('transform: %s'%sox_transform.effects)
            input_file = _pathname(audio_tempfile)
            out_file = _pathname(out_tf)
            logger.debug('sox in and out files: %s %s'%(input_file, out_file))
            status = sox_transform.build(input_file, out_file,
                                                return_output=True )
            logger.debug('sox.build exit code %s'%str(status))
            logger.debug('audio duration  %.2f s'%
                sox.file_info.duration(_pathname(out_tf)))
            logger.debug('video duration  %.2f s'%
                self.videoclip.get_duration())
            return out_tf
        def _meta_wav_dest(p1, p2, p3):
            """
            takes metadata from p1, sound from p2 and combine them to create p3.
            arguments are pathlib.Path or string;
            returns nothing.
            """
            f1, f2, f3 = [_pathname(p) for p in [p1, p2, p3]]
            process_list = ['ffmpeg', '-y', '-loglevel', 'quiet', '-nostats', '-hide_banner',
                    '-i', f1, '-i', f2, '-map', '1',
                    '-map_metadata', '0', '-c', 'copy', f3]
            proc = subprocess.run(process_list)
        logger.debug(f'synced_clip_file raw')
        if snd_root == None:
            # alongside mode
            synced_clip_file = self.videoclip.final_synced_file
            logger.debug('alongside mode')
            synced_clip_dir = synced_clip_file.parent
        else:
            # MAM mode
            synced_clip_file = self.videoclip.AVpath
            logger.debug('MAM mode')
            rel = synced_clip_file.parent.relative_to(raw_root)
            synced_clip_dir = Path(snd_root)/Path(raw_root).name/rel
            logger.debug(f'synced_clip_dir: {synced_clip_dir}')
        # build ISOs subfolders structure, see comment string below
        video_stem_WO_suffix = synced_clip_file.stem
        # ISOdir = synced_clip_dir/(video_stem_WO_suffix + 'ISO')
        ISOdir = synced_clip_dir/(video_stem_WO_suffix + '_SND')/'ISOfiles'
        os.makedirs(ISOdir, exist_ok=True)
        logger.debug('edited_audio_all_devices %s'%edited_audio_all_devices)
        logger.debug('ISOdir %s'%ISOdir)
        for name, mono_tmpfl, device in edited_audio_all_devices:
            logger.debug(f'name:{name} mono_tmpfl:{mono_tmpfl} device:{pformat(device)}')
            destination = ISOdir/(f'{video_stem_WO_suffix}_{name}.wav')
            mono_tmpfl_trimpad = _fit_length(mono_tmpfl)
            # if audio_only, self.ref_audio does not have itself as matching audio
            if audio_only and device == self.ref_audio.device:
                first_rec = self.ref_audio
            else:
                first_rec = self._get_all_recordings_for(device)[0]
            logger.debug(f'will use {first_rec} for metadata source to copy over {destination}')
            _meta_wav_dest(first_rec.AVpath, mono_tmpfl_trimpad, destination)
            # remove_write_permissions(destination)
            logger.debug('destination:%s'%destination)

    def _get_device_mix(self, device, multichan_tmpfl) -> tempfile.NamedTemporaryFile:
        """
        Build or get a mix from edited and joined audio for a given device

        Returns a mix for merging with video clip. The way the mix is obtained
        (or created) depends if a tracks.txt for the device  was submitted and
        depends on its content. There are 4 cases (explained later):

        #1 no mix (or no tracks.txt), all mono
        #2 no mix, one or more stereo mics
        #3 mono mix declared
        #4 stereo mix declared

        In details:

        If no device tracks.txt file declared a mix track (or if tracks.txt is
        absent) a mix is done programmatically. Two possibilities:

            #1- no stereo pairs were declared: a global mono mix is returned.
            #2- one or more stereo pair mics were used and declared (micL, micR):
            a global stereo mix is returned with mono tracks panned 50-50

        If device has an associated Tracks description AND it declares a (mono or
        stereo) mix track, this fct returns a tempfile containing the
        corresponding tracks, simply extracting them from multichan_tmpfl
        (those covers cases #3 and #4)

        Args:
            device : device_scanner.Device dataclass
                the device that recorded the audio found in multichan_tmpfl
            multichan_tmpfl : tempfile.NamedTemporaryFile
                contains the edited and synced audio, almost ready to be merged
                with the concurrent video file (after mix down)

        Returns:
            the tempfile.NamedTemporaryFile of a stereo or mono wav file
            containing the audio to be merged with the video in
            self.videoclip


        """
        logger.debug('device %s'%device)
        if device.n_chan == 2:
            # tracks.txt or not,
            # it's stereo, ie audio + TTC, so remove TTC and return
            kept_channel = (device.ttc + 1)%2 # 1 -> 0 and 0 -> 1
            logger.debug('no tracks.txt, keeping one chan %i'%kept_channel)
            return _sox_keep(multichan_tmpfl, [kept_channel + 1]) #-------------
        logger.debug('device.n_chan != 2, so multitrack')
        # it's multitrack (more than 2 channels)
        if device.tracks is None:
            # multitrack but no mix done on location, so do mono mix with all
            all_channels = list(range(device.n_chan))
            logger.debug('multitrack but no tracks.txt, mixing %s except TTC at %i'%
                (all_channels, device.ttc))
            all_channels.remove(device.ttc)
            sox_kept_channels = [i + 1 for i in all_channels] # sox indexing
            logger.debug('mixing channels: %s (sox #)'%sox_kept_channels)
            kept_audio = _sox_keep(multichan_tmpfl, sox_kept_channels)
            return _sox_mix_channels(kept_audio) #------------------------------
        logger.debug('there IS a device.tracks')
        # user wrote a tracks.txt metadata file, check it to get the mix(or do
        # it). But first a check is done if the ttc tracks concur: the track
        # detected by the Decoder class, stored in device.ttc VS the track
        # declared by the user, device.tracks.ttc (see device_scanner.py). If
        # not, warn the user and exit.
        logger.debug('ttc channel declared for the device: %i, ttc detected: %i, non zero base indexing'%
                        (device.ttc, device.tracks.ttc))
        if device.ttc + 1 != device.tracks.ttc: # warn and quit
            print('Error: TicTacCode channel detected is [gold1]%i[/gold1]'%
                (device.ttc), end=' ')
            print('and [gold1]%s[/gold1] for the device [gold1]%s[/gold1] specifies channel [gold1]%i[/gold1],'%
                (device_scanner.TRACKSFILE,
                device.name, device.tracks.ttc-1))
            print('Please correct the discrepancy and rerun. Quitting.')
            sys.exit(1)
        if device.tracks.mix == [] and device.tracks.stereomics == []:
            # it's multitrac and no mix done on location, so do a mono mix with
            # all, but here remove '0' and TTC tracks from mix
            all_channels = list(range(1, device.n_chan + 1)) # sox not ZBIDX
            to_remove = device.tracks.unused + [device.ttc+1]# unused is sox idx
            logger.debug('multitrack but no mix, mixing mono %s except # %s (sox #)'%
                (all_channels, to_remove))
            sox_kept_channels = [i for i in all_channels
                                            if i not in to_remove]
            logger.debug('mixing channels: %s (sox #)'%sox_kept_channels)
            kept_audio = _sox_keep(multichan_tmpfl, sox_kept_channels)
            return _sox_mix_channels(kept_audio) #------------------------------
        logger.debug('device.tracks.mix != [] or device.tracks.stereomics != []')
        if device.tracks.mix != []:
            # Mix were done on location, no and we only have to extracted it
            # from the recording. If mono mix, device.tracks.mix has one element;
            # if stereo mix, device.tracks.mix is a pair of number:
            logger.debug('%s has mix %s'%(device.name, device.tracks.mix))
            logger.debug('device %s'%device)
            # just checking coherency
            if 'tc' in device.tracks.rawtrx:
                trx_TTC_chan = device.tracks.rawtrx.index('tc')
            elif 'TC' in device.tracks.rawtrx:
                trx_TTC_chan = device.tracks.rawtrx.index('TC')
            else:
                print('Error: no tc or ttc tag in track.txt')
                print(device.tracks.rawtrx)
                sys.exit(1)
            logger.debug('TTC chan %i, dev ttc %i'%(trx_TTC_chan, device.ttc))
            if trx_TTC_chan != device.ttc:
                print('Error: ttc channel # incoherency in track.txt')
                sys.exit(1)
            # coherency check done, extract mix track (or tracks if stereo)
            mix_kind = 'mono' if len(device.tracks.mix) == 1 else 'stereo'
            logger.debug('%s mix declared on channel %s (sox #)'%
                    (mix_kind, device.tracks.mix))
            return _sox_keep(multichan_tmpfl, device.tracks.mix) #--------------
        logger.debug('device.tracks.mix == []')
        # if here, all cases have been covered, all is remaining is this case:
        # tracks.txt exists  AND there is no mix AND stereo mic(s) so first a
        # coherency check, and then proceed
        if device.tracks.stereomics == []:
            print('Error, no stereo mic?, check tracks.txt. Quitting')
            sys.exit(1)
        logger.debug('processing stereo pair(s) %s'%device.tracks.stereomics)
        stereo_mic_idx_pairs = [pair for name, pair in device.tracks.stereomics]
        logger.debug('stereo pairs idxs %s'%stereo_mic_idx_pairs)
        mic_stereo_files = [_sox_keep(multichan_tmpfl, pair) for pair
                                                    in stereo_mic_idx_pairs]
        # flatten list of tuples of channels being stereo mics
        stereo_mic_idx_flat = [item for sublist in stereo_mic_idx_pairs
                                                    for item in sublist]
        logger.debug('stereo_mic_idx_flat %s'%stereo_mic_idx_flat)
        mono_tracks = [i for i in range(1, device.n_chan + 1)
                                if i not in stereo_mic_idx_flat]
        logger.debug('mono_tracks (with ttc+zeroed included): %s'%mono_tracks)
        # remove TTC track number
        to_remove = device.tracks.unused + [device.ttc+1]# unused is sox idx
        [mono_tracks.remove(t) for t in to_remove]
        # mono_tracks.remove(device.ttc + 1)
        logger.debug('mono_tracks (ttc+zeroed removed)%s'%mono_tracks)
        mono_files = [_sox_keep(multichan_tmpfl, [chan]) for chan
                                                    in mono_tracks]
        new_stereo_files = [_sox_mono2stereo(f) for f in mono_files]
        stereo_files = mic_stereo_files + new_stereo_files
        return _sox_mix_files(stereo_files)

    # def build_audio_and_write_merged_media(self, top_dir, 
    #                         dont_write_cam_folder, asked_ISOs, audio_REC_only):
    #     # simply bifurcates depending if ref media is video (prob 99%)
    #     # (then audio_REC_only == False)
    #     # or if ref media is audio (no camera detected, 1% of cases)
    #     # (with audio_REC_only == True)
    #     if not audio_REC_only:
    #         # almost always syncing audio to video clips
    #         self._build_audio_and_write_video(top_dir,
    #                                 dont_write_cam_folder, asked_ISOs)
    #     else:
    #         # rare
    #         self._build_and_write_audio(top_dir, anchor_dir)

    def _build_and_write_audio(self, top_dir, anchor_dir=None):
        """
        This is called when only audio recorders were found (no cam).

        top_dir: Path, directory where media were looked for

        anchor_dir: str for optional folder specified as CLI argument, if
        value is None, fall back to OUT_DIR_DEFAULT

        For each audio devices found overlapping self.ref_audio: pad, trim
        or stretch audio files by calling _get_concatenated_audiofile_for(), and
        put them in merged_audio_files_by_device. More than one audio recorder
        can be used for a shot: that's why merged_audio_files_by_device is a
        list.

        Returns nothing

        Sets AudioStitcherVideoMerger.final_synced_file on completion to list
        containing all the synced and patched audio files.
        """
        self.ref_audio = self.videoclip # ref audio was stored in videoclip
        logger.debug('Will merge audio against %s from %s'%(self.ref_audio,
                                                self.ref_audio.device.name))
        # eg, suppose the user called tictacsync with 'mondayPM' as top folder
        # to scan for dailies (and 'somefolder' for output):
        if anchor_dir == None:
            synced_clip_dir = Path(top_dir)/OUT_DIR_DEFAULT # = mondayPM/SyncedMedia
        else:
            synced_clip_dir = Path(anchor_dir)/Path(top_dir).name # = somefolder/mondayPM
        self.synced_clip_dir = synced_clip_dir
        os.makedirs(synced_clip_dir, exist_ok=True)
        logger.debug('synced_clip_dir is: %s'%synced_clip_dir)
        synced_clip_file = synced_clip_dir/self.videoclip.AVpath.name
        logger.debug('editing files for synced_clip_file%s'%synced_clip_file)
        self.ref_audio.final_synced_file = synced_clip_file # relative path
        # Collecting edited audio by device, in (Device, tempfile) pairs:
        # for a given self.ref_audio, each other audio device will have a sequence
        # of matched, synced and joined audio files present in a single
        # edited audio file, returned by _get_concatenated_audiofile_for
        merged_audio_files_by_device = [
                            (d, self._get_concatenated_audiofile_for(d)) 
                            for d in self._get_secondary_audio_devices()]
        # at this point, audio editing has been done in tempfiles
        logger.debug('%i elements in merged_audio_files_by_device'%len(
                                            merged_audio_files_by_device))
        for d, f, in merged_audio_files_by_device:
            logger.debug('device: %s'%d.name)
            logger.debug('file %s of %i channels'%(f.name,
                                        sox.file_info.channels(f.name)))
        logger.debug('')
        if not merged_audio_files_by_device:
            # no audio file overlaps for this clip
            return #############################################################
        logger.debug('will output ISO files since no cam')
        devices_and_monofiles = [(device, _sox_split_channels(multi_chan_audio))
                for device, multi_chan_audio
                in merged_audio_files_by_device]
        # add device and file from self.ref_audio
        new_tuple = (self.ref_audio.device,
                        _sox_split_channels(self.ref_audio.AVpath))
        devices_and_monofiles.append(new_tuple)
        logger.debug('devices_and_monofiles: %s'%
            pformat(devices_and_monofiles))
        def _trnm(dev, idx): # used in the loop just below
            # generates track name for later if asked_ISOs
            # idx is from 0 to nchan-1 for this device
            if dev.tracks == None:
                chan_name = 'chan%s'%str(idx+1).zfill(2)
            else:
                # sanitize
                symbols = set(r"""`~!@#$%^&*()_-+={[}}|\:;"'<,>.?/""")
                chan_name = dev.tracks.rawtrx[idx]
                logger.debug('raw chan_name %s'%chan_name)
                chan_name = chan_name.split(';')[0] # if ex: "lav bob;25"
                logger.debug('chan_name WO ; lag: %s'%chan_name)
                chan_name =''.join([e if e not in symbols else ''
                                    for e in chan_name])
                logger.debug('chan_name WO special chars: %s'%chan_name)
                chan_name = chan_name.replace(' ', '_')
                logger.debug('chan_name WO spaces: %s'%chan_name)
                chan_name += '_' + dev.name # TODO: make this an option?
            logger.debug('track_name %s'%chan_name)
            return chan_name #####################################################
        # replace device, idx pair with track name (+ device name if many)
        # loop over devices than loop over tracks
        names_audio_tempfiles = []
        for dev, mono_tmpfiles_list in devices_and_monofiles:
            for idx, monotf in enumerate(mono_tmpfiles_list):
                track_name = _trnm(dev, idx)
                logger.debug('track_name %s'%track_name)
                if track_name[0] == '0': # muted, skip
                    continue
                names_audio_tempfiles.append((track_name, monotf, dev))
        logger.debug('names_audio_tempfiles %s'%pformat(names_audio_tempfiles))
        self._write_ISOs(names_audio_tempfiles, audio_only=True)
        logger.debug('merged_audio_files_by_device %s'%
                            merged_audio_files_by_device)

    def _build_audio_and_write_video(self, top_dir, dont_write_cam_folder,
                                            asked_ISOs, synced_root = None,
                                            snd_root = None, raw_root = None):
        """
        top_dir: Path, directory where media were looked for

        anchor_dir: str for optional folder specified as CLI argument, if
        value is None, fall back to OUT_DIR_DEFAULT

        dont_write_cam_folder: True if needs to bypass writing multicam folders

        asked_ISOs: bool flag specified as CLI argument

        For each audio devices found overlapping self.videoclip: pad, trim
        or stretch audio files by calling _get_concatenated_audiofile_for(), and
        put them in merged_audio_files_by_device. More than one audio recorder
        can be used for a shot: that's why merged_audio_files_by_device is a
        list

        Returns nothing

        Sets AudioStitcherVideoMerger.final_synced_file on completion
        """
        logger.debug(' fct args: top_dir %s, dont_write_cam_folder %s, asked_ISOs %s'%
            (top_dir, dont_write_cam_folder, asked_ISOs))
        logger.debug('device for rec %s: %s'%(self.videoclip,
            self.videoclip.device))
        if synced_root == None:
            # alongside, within SyncedMedia dirs
            synced_clip_dir = self.videoclip.AVpath.parent/OUT_DIR_DEFAULT
            logger.debug('"alongside mode" for clip: %s'%self.videoclip.AVpath)
            logger.debug(f'will save in {synced_clip_dir}')
        else:
            # MAM mode
            logger.debug('MAM mode')
            synced_clip_dir = Path(synced_root)/str(self.videoclip.AVpath.parent)[1:] # strip leading /
            rel = self.videoclip.AVpath.parent.relative_to(raw_root).parent
            logger.debug(f'relative path {rel}')
            synced_clip_dir = Path(synced_root)/Path(raw_root).name/rel
            logger.debug(f'will save in {synced_clip_dir}')
        self.synced_clip_dir = synced_clip_dir
        os.makedirs(synced_clip_dir, exist_ok=True)
        # logger.debug('synced_clip_dir is: %s'%synced_clip_dir)
        synced_clip_file = synced_clip_dir/self.videoclip.AVpath.name
        logger.debug('editing files for synced_clip_file %s'%synced_clip_file)
        self.videoclip.final_synced_file = synced_clip_file # relative path
        # Collecting edited audio by device, in (Device, tempfiles) pairs:
        # for a given self.videoclip, each audio device will have a sequence
        # of matched, synced and joined audio files present in a single
        # edited audio file, returned by _get_concatenated_audiofile_for
        merged_audio_files_by_device = [
                            (d, self._get_concatenated_audiofile_for(d)) 
                            for d in self._get_audio_devices()]
        # at this point, audio editing has been done in multichan wav tempfiles 
        logger.debug('merged_audio_files_by_device %s'%merged_audio_files_by_device)
        for d, f, in merged_audio_files_by_device:
            logger.debug('%s'%d)
            logger.debug('file %s'%f.name)
        if len(merged_audio_files_by_device) == 0:
            # no audio file overlaps for this clip
            return #############################################################
        if len(merged_audio_files_by_device) == 1:
            # only one audio recorder was used, pick singleton in list
            dev, concatenate_audio_file = merged_audio_files_by_device[0]
            logger.debug('one audio device only: %s'%dev)
            # check if this sole recorder is stereo
            if dev.n_chan == 2:
                # consistency check
                nchan_sox = sox.file_info.channels(
                    _pathname(concatenate_audio_file))
                logger.debug('Two chan only, nchan_sox: %i dev.n_chan %i'%
                                (nchan_sox, dev.n_chan))
                if not nchan_sox == 2:
                    raise Exception('Error in channel processing')
                # all OK, merge and return
                logger.debug('simply mono to merge, TTC on chan %i'%
                            dev.ttc)
                # only 2 channels so keep the channel OTHER than TTC
                if dev.ttc == 1:
                    # keep channel 0, but + 1 because of sox indexing
                    sox_kept_channel = 1 
                else:
                    # dev.ttc == 0 so keep ch 1, but + 1 (sox indexing)
                    sox_kept_channel = 2
                self.videoclip.synced_audio = \
                        _sox_keep(concatenate_audio_file, [sox_kept_channel])
                self._merge_audio_and_video()
                if asked_ISOs:
                    print('WARNING: you asked for ISO files but found one audio channel only...')
                return #########################################################
        #
        # if not returned yet from fct, either multitracks and/or multi
        # recorders so check if a mix has been done on location and identified
        # as is in atracks.txt file. Split audio channels in mono wav tempfiles
        # at the same time
        #
        multiple_recorders = len(merged_audio_files_by_device) > 1
        logger.debug('multiple_recorder: %s'%multiple_recorders)
        # the device_mixes list contains all audio recorders if many. If only
        # one audiorecorder was used (most of the cases) len(device_mixes) is 1
        device_mixes = [self._get_device_mix(device, multi_chan_audio)
                for device, multi_chan_audio
                in merged_audio_files_by_device]
        logger.debug('there are %i dev device_mixes'%len(device_mixes))
        logger.debug('device_mixes %s'%device_mixes)
        mix_of_device_mixes = _sox_mix_files(device_mixes)
        logger.debug('will merge with %s'%(_pathname(mix_of_device_mixes)))
        self.videoclip.synced_audio = mix_of_device_mixes
        logger.debug('mix_of_device_mixes (final mix) has %i channels'%
            sox.file_info.channels(_pathname(mix_of_device_mixes)))
        self._merge_audio_and_video()
        # devices_and_monofiles is list of (device, [monofiles])
        # [(dev1, multichan1), (dev2, multichan2)] in
        # merged_audio_files_by_device -> 
        # [(dev1, [mono1_ch1, mono1_ch2]), (dev2, [mono2_ch1, mono2_ch2)]] in 
        # devices_and_monofiles:
        if asked_ISOs:
            logger.debug('will output ISO files...')
            devices_and_monofiles = [(device, _sox_split_channels(multi_chan_audio))
                    for device, multi_chan_audio
                    in merged_audio_files_by_device]
            logger.debug('devices_and_monofiles: %s'%
                pformat(devices_and_monofiles))
            def _build_from_tracks_txt(dev, idx):
                # used in the loop just below
                # generates track name for later if asked_ISOs
                # idx is from 0 to nchan-1 for this device
                if dev.tracks == None:
                    # no tracks.txt was found so use ascending numbers for name
                    chan_name = 'chan%s'%str(idx+1).zfill(2)
                else:
                    # sanitize names in tracks.txt
                    symbols = set(r"""`~!@#$%^&*()_-+={[}}|\:;"'<,>.?/""")
                    chan_name = dev.tracks.rawtrx[idx]
                    logger.debug('raw chan_name %s'%chan_name)
                    chan_name = chan_name.split(';')[0] # if ex: "lav bob;25"
                    logger.debug('chan_name WO ; lag: %s'%chan_name)
                    chan_name =''.join([e if e not in symbols else ''
                                        for e in chan_name])
                    logger.debug('chan_name WO special chars: %s'%chan_name)
                    chan_name = chan_name.replace(' ', '_')
                    logger.debug('chan_name WO spaces: %s'%chan_name)
                if multiple_recorders:
                    chan_name += '_' + dev.name # TODO: make this an option?
                logger.debug('track_name %s'%chan_name)
                return chan_name #####################################################
            # replace device, idx pair with track name (+ device name if many)
            # loop over devices than loop over tracks
            names_audio_tempfiles = []
            for dev, mono_tmpfiles_list in devices_and_monofiles:
                for idx, monotf in enumerate(mono_tmpfiles_list):
                    track_name = _build_from_tracks_txt(dev, idx)
                    logger.debug('track_name %s'%track_name)
                    if track_name[0] == '0': # muted, skip
                        continue
                    names_audio_tempfiles.append((track_name, monotf, dev))
            logger.debug('names_audio_tempfiles %s'%pformat(names_audio_tempfiles))
            self._write_ISOs(names_audio_tempfiles,
                snd_root=snd_root, synced_root=synced_root, raw_root=raw_root)
        logger.debug('merged_audio_files_by_device %s'%
            merged_audio_files_by_device)
        # This loop below for logging purpose only:
        for idx, pair in enumerate(merged_audio_files_by_device):
            # dev_joined_audio is mono, stereo or even polywav from multitrack 
            # recorders. For one video there could be more than one dev_joined_audio
            # if multiple audio recorders where used during the take.
            # this loop is for one device at the time.
            device, dev_joined_audio = pair
            logger.debug('idx: % i device.folder: %s'%(idx, device.folder))
            nchan = sox.file_info.channels(_pathname(dev_joined_audio))
            logger.debug('dev_joined_audio: %s nchan:%i'%
                (_pathname(dev_joined_audio), nchan))
            logger.debug('duration %f s'%
                sox.file_info.duration(_pathname(dev_joined_audio)))

    def _keep_VIDEO_only(self, video_path):
        # return file handle to a temp video file formed from the video_path
        # stripped of its sound
        in1 = ffmpeg.input(_pathname(video_path))
        video_extension = video_path.suffix
        silenced_opts = ["-loglevel", "quiet", "-nostats", "-hide_banner"]
        file_handle = tempfile.NamedTemporaryFile(suffix=video_extension,
            delete=DEL_TEMP)
        out1 = in1.output(file_handle.name, map='0:v', vcodec='copy')
        ffmpeg.run([out1.global_args(*silenced_opts)], overwrite_output=True)
        return file_handle

    def _merge_audio_and_video(self):
        """      
        Calls ffmpeg to join video in self.videoclip.AVpath to
        audio in self.videoclip.synced_audio. Audio in original video
        is dropped.

        On entry, videoclip.final_synced_file is a Path to an non existing
        file (contrarily to videoclip.synced_audio).
        On exit, self.videoclip.final_synced_file points to the final synced
        video file.

        Returns nothing.
        """
        synced_clip_file = self.videoclip.final_synced_file
        video_path = self.videoclip.AVpath
        timecode = self.videoclip.get_start_timecode_string()
        # self.videoclip.synced_audio = audio_path
        audio_path = self.videoclip.synced_audio
        vid_only_handle = self._keep_VIDEO_only(video_path)
        a_n = _pathname(audio_path)
        v_n = str(vid_only_handle.name)
        out_n = str(synced_clip_file)
        logger.debug('Merging: \n\t %s + %s = %s\n'%(
                        audio_path,
                        video_path,
                        synced_clip_file
                        ))
        # building args for debug purpose only:
        ffmpeg_args = (
            ffmpeg
            .input(v_n)
            # .output(out_n, shortest=None, vcodec='copy',
            .output(out_n, vcodec='copy',
                timecode=timecode)
            .global_args('-i', a_n, "-hide_banner")
            .overwrite_output()
            .get_args()
        )
        logger.debug('ffmpeg args: %s'%' '.join(ffmpeg_args))
        try: # for real now
            _, out = (
            ffmpeg
            .input(v_n)
            .output(out_n, vcodec='copy',
            # .output(out_n, shortest=None, vcodec='copy',
                # metadata='reel_name=foo', not all container support gen MD
                timecode=timecode,
                )
            .global_args('-i', a_n, "-hide_banner")
            .overwrite_output()
            .run(capture_stderr=True)
            )
            logger.debug('ffmpeg output')
            for l in out.decode("utf-8").split('\n'):
                logger.debug(l)
        except ffmpeg.Error as e:
            print('ffmpeg.run error merging: \n\t %s + %s = %s\n'%(
                audio_path,
                video_path,
                synced_clip_file
                ))
            print(e)
            print(e.stderr.decode('UTF-8'))
            sys.exit(1)

class Matcher:
    """
    Matcher looks for any video in self.recordings and for each one finds out
    all audio recordings (again in self.recordings) that time overlap
    (or against any designated 'main sound', see below). It then spawns
    AudioStitcherVideoMerger objects that do the actual file manipulations. Each video
    (and main sound) will have its AudioStitcherVideoMerger instance.

    The Matcher doesn't keep neither set any editing information in itself: the
    in and out time values (UTC times) used are those kept inside each Recording
    instances.

    Attributes:

        recordings : list of Recording instances
            all the scanned recordings with valid TicTacCode, set in __init__()

        mergers : list
            of AudioStitcherVideoMerger Class instances, built by
            scan_audio_for_each_videoclip(); each video has a corresponding
            AudioStitcherVideoMerger object. An audio_stitch doesn't extend
            beyond the corresponding video start and end times.

        multicam_clips_clusters : list
            of  {'end': t1, 'start': t2, 'vids': [r1,r3]} where r1 and r3
            are overlapping.

    """

    def __init__(self, recordings_list):
        """        
        At this point in the program, all recordings in recordings_list should
        have a valid Recording.start_time attribute and one of its channels
        containing a TicTacCode signal (which the start_time has been demodulated
        from)
        
        """
        self.recordings = recordings_list
        self.mergers = []

    def scan_audio_for_each_videoclip(self):
        """
        For each video (and for the Main Sound) in self.recordings, this finds
        any audio that has overlapping times and instantiates a
        AudioStitcherVideoMerger object.

        V1 checked against A1, A2, A3, A4
        V2 checked against A1, A2, A3, A4
        V3 checked against    ...
        Main Sound checked against A1, A2, A3, A4
        """
        video_recordings = [r for r in self.recordings
                        if r.is_video() or r.is_audio_reference]
        # if r.is_audio_reference then audio, and will pass as video                
        audio_recs = [r for r in self.recordings if r.is_audio()
                                                and not r.is_audio_reference]
        if not audio_recs:
            print('\nNo audio recording found, syncing of videos only not implemented yet, exiting...\n')
            sys.exit(1)
        for videoclip in video_recordings:
            reference_tag = 'video' if videoclip.is_video() else 'audio'
            logger.debug('Looking for overlaps with %s %s'%(
                            reference_tag,
                            videoclip))
            audio_stitch = AudioStitcherVideoMerger(videoclip)
            for audio in audio_recs:
                logger.debug('checking %s'%audio)
                if self._does_overlap(videoclip, audio):
                    audio_stitch.add_matched_audio(audio)
                    logger.debug('recording %s overlaps,'%(audio))
                    # print('  recording [gold1]%s[/gold1] overlaps,'%(audio))
            if len(audio_stitch.get_matched_audio_recs()) > 0:
                self.mergers.append(audio_stitch)
            else:
                logger.debug('\n  nothing\n')
                print('No overlap found for [gold1]%s[/gold1]'%videoclip.AVpath.name)
                del audio_stitch
        logger.debug('%i mergers created'%len(self.mergers))

    def _does_overlap(self, videoclip, audio_rec):
        A1, A2 = audio_rec.get_start_time(), audio_rec.get_end_time()
        logger.debug('audio str stp: %s %s'%(A1,A2))
        R1, R2 = videoclip.get_start_time(), videoclip.get_end_time()
        logger.debug('video str stp: %s %s'%(R1,R2))
        case1 = A1 < R1 < A2
        case2 = A1 < R2 < A2
        case3 = R1 < A1 < R2
        case4 = R1 < A2 < R2
        return case1 or case2 or case3 or case4

    def set_up_clusters(self):
        # builds the list self.multicam_clips_clusters. A list 
        # of  {'end': t1, 'start': t2, 'vids': [r1,r3]} where r1 and r3
        # are overlapping.
        # if no overlap occurs, length of vid = 1, ex 'vids': [r1]
        # so not really a cluster in those cases
        # returns nothing and sets Matcher.multicam_clips_clusters
        vids = [m.videoclip for m in self.mergers]
        # INs_and_OUTs contains (time, direction, video) for each video,
        # where direction is 'in|out' and video an instance of Recording
        INs_and_OUTs = [(vid.get_start_time(), 'in', vid) for vid in vids]
        for vid in vids:
            INs_and_OUTs.append((vid.get_end_time(), 'out', vid))
        INs_and_OUTs = sorted(INs_and_OUTs, key=lambda vtuple: vtuple[0])
        logger.debug('INs_and_OUTs: %s'%pformat(INs_and_OUTs))
        new_cluster = True
        current_cluster = {'vids':[]}
        N_in, N_out = (0, 0)
        # clusters is a list of  {'end': t1, 'start': t2, 'vids': [r1,r3]}
        clusters = []
        # a cluster begins (and grows) when a time of type 'in' is encountered
        # a cluster degrows when a time of type 'out' is encountered and
        # closes when its size (N_currently_open) reach back to zero
        for t, direction, video in INs_and_OUTs:
            if new_cluster and direction == 'out':
                logger.error('cant begin a cluster with a out time %s'%video)
                sys.exit(1)
            if new_cluster:
                current_cluster['start'] = t
                new_cluster = False
            if direction == 'in':
                N_in += 1
                current_cluster['vids'].append(video)
            else:
                N_out += 1
            N_currently_open = N_in - N_out
            if N_currently_open == 0:
                # print(t,direction,video)
                current_cluster['end'] = t
                clusters.append(current_cluster)
                new_cluster = True
                current_cluster = {'vids':[]}
                N_in, N_out = (0, 0)
        logger.debug('clusters: %s'%pformat(clusters))
        self.multicam_clips_clusters = clusters
        return

    def shrink_gaps_between_takes(self, CLI_offset, with_gap=CLUSTER_GAP):
        """
        for single cam shootings this simply sets the gap between takes,
        tweaking each vid timecode metadata to distribute them next to each
        other along NLE timeline.

        Moves clusters at the timelineoffset

        For multicam takes, shifts are computed so
        video clusters are near but dont overlap, ex: 

        ***** are inserted gaps

        Cluster 1                    Cluster 2
        1111111111111                 2222222222 (cam A)
           11111111111******222222222 (cam B)

        or
        11111111111111          222222 (cam A)
          1111111     ******222222222 (cam B)

        argument:
            CLI_offset (str), option from command-line
            with_gap (float), the gap duration in seconds

        Returns nothing, changes are done in the video files metadata
        (each referenced by Recording.final_synced_file)
        """
        vids = [m.videoclip for m in self.mergers]
        logger.debug('vids %s'%vids)
        if len(vids) == 1:
            logger.debug('just one take, no gap to shrink')
            return #############################################################
        clusters = self.multicam_clips_clusters
        # if there are N clusters, there are N-1 gaps to evaluate and shorten
        # (lengthen?) to a value of with_gap seconds
        gaps = [c2['start'] - c1['end'] for c1, c2
                                    in zip(clusters, clusters[1:])]
        logger.debug('gaps between clusters %s'%[g.total_seconds()
            for g in gaps])
        logger.debug('desired gap is %f'%with_gap)
        # if gap is 3.5s and goal is 2s (the with_gap parameter), clip has to
        # move 1.5s *to the left* ie towards negative axis of time, so the
        # offset should be negative too
        offsets = [timedelta(seconds=with_gap) - gap for gap in gaps]
        logger.debug('gap difference: %s'%[o.total_seconds() for o in offsets])
        zero = [timedelta(seconds=0)] # for the first cluster
        cummulative_offsets = zero + list(numpy.cumsum(offsets))
        # for now on, offsets are in secs, not timedeltas
        cummulative_offsets = [td.total_seconds() for td in cummulative_offsets]
        logger.debug('cummulative_offsets: %s'%cummulative_offsets)
        time_of_first = clusters[0]['start']
        # compute CLI_offset_in_seconds from HH:MM:SS:FF in CLI_offset
        h, m, s, f = [float(s) for s in CLI_offset[0].split(':')]
        logger.debug('CLI_offset float values %s'%[h,m,s,f])
        CLI_offset_in_seconds = 3600*h + 60*m + s + f/vids[0].get_framerate()
        logger.debug('CLI_offset in seconds %f'%CLI_offset_in_seconds)
        offset_for_all_clips = - from_midnight(time_of_first).total_seconds()
        offset_for_all_clips += CLI_offset_in_seconds
        logger.debug('time_of_first: %s'%time_of_first)
        logger.debug('offset_for_all_clips: %s'%offset_for_all_clips)
        for cluster, offset in zip(clusters, cummulative_offsets):
            # first one starts at 00:00:00:00
            total_offset = offset + offset_for_all_clips
            logger.debug('for %s offset in sec: %f'%(cluster['vids'],
                    total_offset))
            for vid in cluster['vids']:
                # tc = vid.get_start_timecode_string(CLI_offset, with_offset=total_offset)
                tc = vid.get_start_timecode_string(with_offset=total_offset)
                logger.debug('for %s old tc: %s new tc %s'%(vid,
                    vid.get_start_timecode_string(), tc))
                vid.write_file_timecode(tc)
        return

    def move_multicam_to_dir(self, raw_root=None, synced_root=None):
        # creates a dedicated multicam directory and move clusters there
        # e.g., for "top/day01/camA/roll02"
        #                       ^  at that level
        #            0   1     2    3
        # Note: ROLLxx maybe present or not.
        #
        # check for consistency: are all clips at the same level from topdir?
        # Only for video, not audio (which doesnt fill up cards)
        logger.debug(f'synced_root: {synced_root}')
        video_medias = [m for m in self.recordings if m.device.dev_type == 'CAM']
        video_paths = [m.AVpath.parts for m in video_medias]
        AV_path_lengths = [len(p) for p in video_paths]
        # print('AV_path_lengths', AV_path_lengths)
        if not _same(AV_path_lengths):
            print('\nError with some clips, check if their locations are consistent (all at the same level in folders).')
            print('Video synced but could not regroup multicam clips.')
            sys.exit(0)
        # now find at which level CAMs reside (maybe there are ROLLxx)
        CAM_levels = [vm.AVpath.parts.index(vm.device.name)
                            for vm in video_medias]
        # find for all, should be same
        if not _same(CAM_levels):
            print('\nError with some clips, check if their locations are consistent (all at the same level in folders).')
            print('Video synced but could not regroup multicam clips.')
            sys.exit(0)
        # pick first
        CAM_level, avp = CAM_levels[0], video_medias[0].AVpath
        logger.debug('CAM_levels: %s for %s\n'%(CAM_level, avp))
        # MCCDIR = 'SyncedMulticamClips'
        parts_up_a_level = [prt for prt in avp.parts[:CAM_level] if prt != '/']
        logger.debug(f'parts_up_a_level: {parts_up_a_level}')
        if synced_root == None:
            # alongside mode
            logger.debug('alongside mode')
            multicam_dir = Path('').joinpath(*parts_up_a_level)/MCCDIR
        else:
            # MAM mode
            logger.debug('MAM mode')
            abs_path_up = Path('/').joinpath(*parts_up_a_level)/MCCDIR
            logger.debug(f'abs_path_up: {abs_path_up}')
            rel_up = abs_path_up.relative_to(raw_root)
            logger.debug(f'rel_up: {rel_up}')
            multicam_dir = Path(synced_root)/Path(raw_root).name/rel_up
            # multicam_dir = Path(synced_root).joinpath(*parts_up_a_level)/MCCDIR
        logger.debug('multicam_dir: %s'%multicam_dir)
        Path.mkdir(multicam_dir, exist_ok=True)
        cam_clips = []
        [cam_clips.append(cl['vids']) for cl in self.multicam_clips_clusters]
        cam_clips = _flatten(cam_clips)
        logger.debug('cam_clips: %s'%pformat(cam_clips))
        cam_names = set([r.device.name for r in cam_clips])
        # create new dirs for each CAM
        [Path.mkdir(multicam_dir/cam_name, exist_ok=True)
                        for cam_name in cam_names]
        # move clips there
        if synced_root == None:
            # alongside mode
            for r in cam_clips:
                cam = r.device.name
                clip_name = r.AVpath.name
                dest = r.final_synced_file.replace(multicam_dir/cam/clip_name)
                logger.debug('dest: %s'%dest)
                origin_folder = r.final_synced_file.parent
                folder_now_empty = len(list(origin_folder.glob('*'))) == 0
                if folder_now_empty:
                    logger.debug('after moving %s, folder is now empty, removing it'%dest)
                    origin_folder.rmdir()
            print('\nMoved %i multicam clips in %s'%(len(cam_clips), multicam_dir))
        else:
            # MAM mode
            for r in cam_clips:
                cam = r.device.name
                clip_name = r.AVpath.name
                dest = r.final_synced_file.replace(multicam_dir/cam/clip_name)
                # leave a symlink behind
                os.symlink(multicam_dir/cam/clip_name, r.final_synced_file)
                logger.debug('dest: %s'%dest)
                origin_folder = r.final_synced_file.parent
                # folder_now_empty = len(list(origin_folder.glob('*'))) == 0
                # if folder_now_empty:
                #     logger.debug('after moving %s, folder is now empty, removing it'%dest)
                #     origin_folder.rmdir()
            print('\nMoved %i multicam clips in %s'%(len(cam_clips), multicam_dir))

        
















