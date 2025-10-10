
# cd /home/lutzray/SyncQUO/Dev/AtomicSync/Sources/PostProduction/tictacsync/tictacsync
# while inotifywait --recursive -e close_write . ; do python entry.py  tests/multi2/; done
# above for linux

TRACKSFILE = 'tracks.txt'
SILENT_TRACK_TOKENS = '-0n'

av_file_extensions = \
"""webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp aa aac aax act aiff alac
amr ape au awb dss dvf flac gsm iklax ivs m4a m4b m4p mmf mp3 mpc msv nmf
ogg oga mogg opus ra rm raw rf64 sln tta voc vox wav wma wv webm 8svx cda MOV AVI
WEBM MKV FLV FLV VOB OGV OGG DRC GIF GIFV MNG AVI MTS M2TS TS MOV QT
WMV YUV RM RMVB VIV ASF AMV MP4 M4P M4V MPG MP2 MPEG MPE MPV MPG MPEG M2V
M4V SVI 3GP 3G2 MXF ROQ NSV FLV F4V F4P F4A F4B 3GP AA AAC AAX ACT AIFF ALAC
AMR APE AU AWB DSS DVF FLAC GSM IKLAX IVS M4A M4B M4P MMF MP3 MPC MSV NMF
OGG OGA MOGG OPUS RA RM RAW RF64 SLN TTA VOC VOX WAV WMA WV WEBM 8SVX CDA MOV AVI BWF""".split()

audio_ext = 'aiff wav mp3'.split()

from dataclasses import dataclass
import ffmpeg, os, sys, shutil
from os import listdir
from os.path import isfile, join, isdir
from collections import namedtuple
from pathlib import Path
from pprint import pformat 
# from collections import defaultdict
from loguru import logger
# import pathlib, os.path
import sox, tempfile, platformdirs, filecmp
# from functools import reduce
from rich import print
from itertools import groupby
# from sklearn.cluster import AffinityPropagation
# import distance
try:
    from . import multi2polywav
    from . import mamsync
    from . import mamconf
except:
    import multi2polywav
    import mamsync
    import mamconf

MCCDIR = 'SyncedMulticamClips'
SYNCEDFOLDER = 'SyncedMedia'

# utility for accessing pathnames
def _pathname(tempfile_or_path):
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

def print_grby(grby):
    for key, keylist in grby:
        print('\ngrouped by %s:'%key)
        for e in keylist:
            print(' ', e)

@dataclass
class Tracks:
    # track numbers start at 1 for first track (as needed by sox)
    ttc: int # track number of TicTacCode signal
    unused: list # of unused tracks
    stereomics: list # of stereo mics track tuples (Lchan#, Rchan#)
    mix: list # of mixed tracks, if a pair, order is L than R
    others: list #of all other tags: (tag, track#) tuples
    rawtrx: list # list of strings read from file
    error_msg: str # 'None' if none
    lag_values: list # list of lag in ms, entry is None if not specified. 

@dataclass
class Device:
    UID: int
    folder: Path # media's parent folder
    name: str
    dev_type: str # CAM or REC
    n_chan: int
    ttc: int # zero based index?
    tracks: Tracks
    sampling_freq: float # fps if cam
    def __hash__(self):
        return self.UID
    def __eq__(self, other):
        return self.UID == other

@dataclass
class Media:
    """A custom data type that represents data for a media file.
    """
    path: Path
    device: Device

def media_at_path(input_structure, p):
    # return Media object for mediafile using ffprobe
    dev_UID, dt, sf = get_device_ffprobe_UID(p)
    dev_name = None
    logger.debug('ffprobe dev_UID:%s dt:%s sf:%s'%(dev_UID, dt,sf))
    if input_structure == 'ordered':
        dev_name = p.parent.name
        if dev_UID is None:
            dev_UID = hash(dev_name)
    if dt == 'CAM':
        streams = ffmpeg.probe(p)['streams']
        audio_streams = [
            stream 
            for stream
            in streams
            if stream['codec_type']=='audio'
            ]
        if len(audio_streams) > 1:
            print('\nfor [gold1]%s[/gold1], ffprobe gave multiple audio streams, quitting.'%p)
            quit()
            # raise Exception('ffprobe gave multiple audio streams?')
        if len(audio_streams) == 0:
            print('ffprobe gave no audio stream for [gold1]%s[/gold1], quitting.'%p)
            quit()
            # raise Exception('ffprobe gave no audio stream for %s, quitting'%p)
        audio_str = audio_streams[0]
        n = audio_str['channels']
        # pprint(ffmpeg.probe(p))
    else:
        n = sox.file_info.channels(_pathname(p)) # eg 2
    logger.debug('for file %s dev_UID established %s'%(p.name, dev_UID))
    device = Device(UID=dev_UID, folder=p.parent, name=dev_name, dev_type=dt,
                n_chan=n, ttc=None, sampling_freq=sf, tracks=None)
    logger.debug('for path: %s, device:%s'%(p,device))
    return Media(p, device)

def get_device_ffprobe_UID(file):
    """
    Tries to find an unique hash integer identifying the device that produced
    the file based on the string inside ffprobe metadata  without any
    reference to date, location, length or time. Find out with ffprobe the type
    of device: CAM or REC for videocamera or audio recorder.

    Device UIDs are used later in Montage._get_concatenated_audiofile_for()
    for grouping each audio or video clip along its own timeline track.
    
    Returns a tuple: (UID, CAM|REC, sampling_freq)
    
    If an ffmpeg.Error occurs, returns (None, None)
    if no UID is found, but device type is identified, returns (None, CAM|REC)

    """
    file = Path(file)
    logger.debug('trying to find UID probe for %s'%file)
    try:
        probe = ffmpeg.probe(file)
    except ffmpeg.Error as e:
        print('ffmpeg.probe error')
        print(e.stderr, file)
        return None, None #-----------------------------------------------------
        # fall back to folder name
    logger.debug('ffprobe %s'%probe)
    streams = probe['streams']
    video_streams = [st for st in streams if st['codec_type'] == 'video']
    audio_streams = [st for st in streams if st['codec_type'] == 'audio']
    if len(video_streams) > 1:
        print('\nmore than one video stream for %s... quitting'%file)
        quit()
    if len(audio_streams) != 1:
        print('\nnbr of audio stream for %s not 1 ... quitting'%file)
        quit()
    codecs = [stream['codec_type'] for stream in streams]
    # cameras have two streams: video AND audio
    device_type = 'CAM' if len(video_streams) == 1 else 'REC'
    if device_type == 'CAM':
        sampling_freq = eval(video_streams[0]['r_frame_rate'])
    else:
        sampling_freq = float(audio_streams[0]['sample_rate'])        
    format_dict = probe['format'] # all files should have this
    if 'tags' in format_dict:
        probe_string = pformat(format_dict['tags'])
        probe_lines = [l for l in probe_string.split('\n') 
                if '_time' not in l 
                and 'time_' not in l 
                and 'location' not in l 
                and 'date' not in l ]
        # this removes any metadata related to the file
        # but keeps metadata related to the device
        logger.debug('probe_lines %s'%probe_lines)
        UID = hash(''.join(probe_lines))
    else:
        UID = None
    if UID == 0: # empty probe_lines from Audacity ?!?
        UID = None
    logger.debug('ffprobe_UID is: %s'%UID)
    return UID, device_type, sampling_freq

class Scanner:
    """
    Class that encapsulates scanning of the directory given as CLI argument.
    Depending on the input_structure detected (loose|ordered), enforce
    some directory structure (or not). Build a list of media files found and a
    try to indentify uniquely the device used to record each media file.

    Attributes:

        input_structure: string
            Any of:
                'loose'
                    all files audio + video are in top folder
                'ordered'
                    eg for multicam on Davinci Resolve
            input_structure is set in scan_media_and_build_devices_UID()

        top_directory : string
            String of path where to start searching for media files.

        # top_dir_has_multicam : bool
        #     If top dir is folder structures AND more than on cam

        found_media_files: list of Media objects
    """

    def __init__(
                    self,
                    top_directory,
                    stay_silent=False,
                ):
        """
        Initialises Scanner

        """
        self.top_directory = top_directory
        self.found_media_files = []
        self.stay_silent = stay_silent

    def get_devices_number(self):
        # how many devices have been found
        return len(set([m.device.UID for m in self.found_media_files]))

    def get_devices(self):
        return set([m.device for m in self.found_media_files])

    def get_media_for_device(self, dev):
        return [m for m in self.found_media_files if m.device == dev]

    def CAM_numbers(self):
        devices = [m.device for m in self.found_media_files]
        CAMs = [d for d in devices if d.dev_type == 'CAM']
        return len(set(CAMs))

    def scan_media_and_build_devices_UID(self, synced_root = None):
        """
        Scans Scanner.top_directory recursively for files with known audio-video
        extensions. For each file found, a device fingerprint is obtained from
        their ffprobe result to ID the device used.

        Also looked for are multifile recordings: files with the exact same
        length. When done, calls

        Returns nothing

        Populates Scanner.found_media_files, a list of Media objects

        Sets Scanner.input_structure = 'loose'|'ordered'

        """
        logger.debug(f'on entry synced_root: {synced_root}')
        if synced_root != None: # mam mode
            p = Path(platformdirs.user_data_dir('mamsync', 'plutz'))/mamconf.LOG_FILE
            with open(p, 'r') as fh:
                done = set(fh.read().split()) # sets of strings of abs path
            logger.debug(f'done clips: {pformat(done)}')
        files = Path(self.top_directory).rglob('*')
        clip_paths = []
        some_done = False
        for raw_path in files:
            if raw_path.suffix[1:] in av_file_extensions:
                if SYNCEDFOLDER not in raw_path.parts: # SyncedMedia
                    if MCCDIR not in raw_path.parts: # SyncedMulticamClips
                        if '_ISO' not in [part[-4:] for part in raw_path.parts]: # exclude ISO wav files
                            if synced_root != None and str(raw_path) in done:
                                logger.debug(f'{raw_path} done')
                                some_done = True
                                continue
                            else:
                                clip_paths.append(raw_path)
        if some_done:
            print('Somme media files were already synced...')
        logger.debug('found media files %s'%clip_paths)
        if len(clip_paths) == 0:
            print('No media found, bye.')
            sys.exit(0)
            # self.found_media_files = []
            # self.input_structure = 'loose'
            # return
        parents = [p.parent for p in clip_paths]
        logger.debug('found parents %s'%pformat(parents))
        # True if all elements are identical
        AV_files_have_same_parent = parents.count(parents[0]) == len(parents)
        logger.debug('AV_files_have_same_parent %s'%AV_files_have_same_parent)
        if AV_files_have_same_parent:
            # all media (video + audio) are in a same folder, so this is loose
            self.input_structure = 'loose'
            # for now (TO DO?) 'loose' == no multi-cam
            # self.top_dir_has_multicam = False
        else:
            # check later if inside each folder, media have same device
            # for now, we'll guess structure is 'ordered'
            self.input_structure = 'ordered'
        for p in clip_paths:
            new_media = media_at_path(self.input_structure, p) # dev UID set here
            self.found_media_files.append(new_media)
        # for non UIDed try building UID from filenam
        def _try_name_from_files(medias):
            # return common first strings in filename
            def _all_identical(a_list):
                return a_list.count(a_list[0]) == len(a_list)
            names = [m.path.name for m in medias]
            transposed_names = list(map(list, zip(*names)))
            same = list(map(_all_identical, transposed_names))
            try:
                first_diff = same.index(False)
            except:
                return names[0].split('.')[0]
            return names[0][:first_diff]
        no_device_UID_medias = [m for m in self.found_media_files
                    if not m.device.UID]
        logger.debug('those media have no device UID %s'%no_device_UID_medias)
        if no_device_UID_medias:
            # will guess a device name from media filenames
            logger.debug('no_device_UID_medias %s'%no_device_UID_medias)
            start_string = _try_name_from_files(no_device_UID_medias)
            if len(start_string) < 2:
                print('\nError, cant identify the device for those files:')
                [print('%s, '%m.path.name, end='') for m in no_device_UID_medias]
                print('\n')
                sys.exit(1)
            one_device = no_device_UID_medias[0].device
            one_device.name = start_string
            if not one_device.UID:
                one_device.UID = hash(start_string)
            print('\nWarning, guessing a device ID for those files:')
            [print('[gold1]%s[/gold1], '%m.path.name, end='') for m
                                            in no_device_UID_medias]
            print('UID: [gold1]%s[/gold1]'%start_string)
            for m in no_device_UID_medias:
                m.device = one_device
            logger.debug('new device added %s'%self.found_media_files)
        logger.debug('Scanner.found_media_files = %s'%pformat(self.found_media_files))
        if self.input_structure == 'ordered':
            self._confirm_folders_have_same_device()
            # self._use_folder_as_device_name()
            devices = set([m.device for m in self.found_media_files])
            audio_devices = [d for d in devices if d.dev_type == 'REC']
            for recorder in audio_devices:
                # process tracks.txt for audio recorders
                recorder.tracks = self._get_tracks_from_file(recorder)
                # logging only:
                if recorder.tracks:
                    if not all([lv == None for lv in recorder.tracks.lag_values]):
                        logger.debug('%s has lag_values %s'%(
                                recorder.name, recorder.tracks.lag_values))
            # check if device is in fact two parents up (and parent = ROLLxx):
            # Group media by folder 2up and verify all media for each
            # group have same device.
            folder2up = lambda m: m.path.parent.parent
            # logger.debug('folder2up: %s'%pformat([folder2up(m) for m
            #                                 in self.found_media_files]))
            medias = sorted(self.found_media_files, key=folder2up)
            # build lists for multiple reference of iterators
            media_grouped_by_folder2up = [ (k, list(iterator)) for k, iterator
                            in groupby(medias, folder2up)]
            logger.debug('media_grouped_by_folder2up: %s'%pformat(
                                            media_grouped_by_folder2up))
            folder_and_UIDs = [(f, [m.device.UID for m in medias])
                        for f, medias in media_grouped_by_folder2up]
            logger.debug('devices: %s'%pformat(folder_and_UIDs))
            def _multiple_and_same(a_list):
                same = a_list.count(a_list[0]) == len(a_list)
                return len(a_list) > 1 and same
            folders_with_same_dev = [(f.name, UIDs[0]) for f, UIDs 
                                            in folder_and_UIDs
                                         if _multiple_and_same(UIDs)]
            logger.debug('folders_with_same_dev: %s'%pformat(folders_with_same_dev))
            for name, UID in folders_with_same_dev:
                for m in self.found_media_files:
                    if m.device.UID == UID:
                        m.device.name = name
        # logger.debug('renamed device media: %s'%pformat(self.found_media_files))
        no_name_devices = [m.device for m in self.found_media_files
                                            if not m.device.name]
                            # possible if self.input_structure == 'loose'
        def _try_name_from_metadata(media): # unused for now
            # search model and make from fprobe
            file = Path(media.path)
            logger.debug('trying to find maker model for %s'%file)
            try:
                probe = ffmpeg.probe(file)
            except ffmpeg.Error as e:
                print('ffmpeg.probe error')
                print(e.stderr, file)
                return None, None #-----------------------------------------------------
                # fall back to folder name
            logger.debug('ffprobe %s'%pformat(probe))
            # [TO BE COMPLETED]
            # could reside in ['format','tags','com.apple.quicktime.model'],
            # or ['format','tags','model'],
            # or ['streams'][0]['tags']['vendor_id'])  :-(
        for anon_dev in no_name_devices:
            medias = self.get_media_for_device(anon_dev)
            guess_name = _try_name_from_files(medias)
            # print('dev %s has no name, guessing %s'%(anon_dev, guess_name))
            logger.debug('dev %s has no name, guessing %s'%(anon_dev, guess_name))
            anon_dev.name = guess_name
        pprint_found_media_files = pformat(self.found_media_files)
        logger.debug('scanner.found_media_files = %s'%pprint_found_media_files)
        logger.debug('all devices %s'%[m.device for m in self.found_media_files])
        dev_is_REC = [m.device.dev_type == 'REC' for m in self.found_media_files]
        if not any(dev_is_REC): # no audio recordings!
            print('\rNo audio recording found, nothing to sync, bye.')
            sys.exit(0)
        # print('devices 312 %s'%set([m.device for m in self.found_media_files]))

    def _get_tracks_from_file(self, device) -> Tracks:
        """        
        Look for eventual track names in TRACKSFILE file, stored inside the
        recorder folder alongside the audio files. If there, returns a Tracks
        object, if not returns None. 
        """        
        source_audio_folder = device.folder
        tracks_file = source_audio_folder/TRACKSFILE
        track_names = False
        a_recording = [m for m in self.found_media_files
                                                if m.device == device][0]
        logger.debug('a_recording for device %s : %s'%(device, a_recording))
        nchan = sox.file_info.channels(str(a_recording.path))
        if os.path.isfile(tracks_file):
            logger.debug('found file: %s'%(TRACKSFILE))
            tracks = self._parse_track_values(tracks_file)
            if tracks.error_msg:
                print('\nError parsing [gold1]%s[/gold1] file: %s, quitting.\n'%
                    (tracks_file, tracks.error_msg))
                sys.exit(1)
            logger.debug('parsed tracks %s'%tracks)
            ntracks = 2*len(tracks.stereomics)
            ntracks += len(tracks.mix)
            ntracks += len(tracks.unused)
            ntracks += len(tracks.others)
            ntracks += 1 # for ttc track
            logger.debug(' n chan: %i n tracks file: %i'%(nchan, ntracks))
            if ntracks != nchan:
                print('\nError parsing %s content'%tracks_file)
                print('incoherent number of tracks, %i vs %i quitting\n'%
                                                    (nchan, ntracks))
                sys.exit(1)
            err_msg = tracks.error_msg
            if  err_msg != None:
                print('\nError, quitting: in file %s, %s'%(tracks_file, err_msg))
                raise Exception
            else:
                logger.debug('tracks object%s'%tracks)
                return tracks
        else:
            logger.debug('no tracks.txt file found')
            return None

    def _confirm_folders_have_same_device(self):
        """
        Since input_structure == 'ordered',
        checks for files in self.found_media_files for structure as following.

        Warns user and quit program for:
          A- folders with mix of video and audio
          B- folders with mix of uniquely identified devices and unUIDied ones
          C- folders with mixed audio an video files
        
        Warns user but proceeds for:
          D- folder with only unUIDied files (overlaps will be check later)
        
        Changes self.input_structure to 'loose' if a folder contains files
        from different devices.

        Proceeds silently if 
          E- all files in the folder are from the same device

        Returns nothing
        """
        def _exit_on_folder_name_clash():
            # Check media parent folders are unique
            # returns media_grouped_by_folder
            def _list_duplicates(seq):
              seen = set()
              seen_add = seen.add
              # adds all elements it doesn't know yet to seen and all other to seen_twice
              seen_twice = set( x for x in seq if x in seen or seen_add(x) )
              # turn the set into a list (as requested)
              return list( seen_twice )
            folder_key = lambda m: m.path.parent
            medias = sorted(self.found_media_files, key=folder_key)
            # build lists for multiple reference of iterators
            media_grouped_by_folder = [ (k, list(iterator)) for k, iterator
                            in groupby(medias, folder_key)]
            logger.debug('media_grouped_by_folder %s'%pformat(
                                                media_grouped_by_folder))
            complete_path_folders = [e[0] for e in media_grouped_by_folder]
            name_of_folders = [p.name for p in complete_path_folders]
            logger.debug('complete_path_folders with media files %s'%
                                                    complete_path_folders)
            logger.debug('name_of_folders with media files %s'%name_of_folders)
            # unique_folder_names = set(name_of_folders) [TODO] is this useful ?
            # repeated_folders = _list_duplicates(name_of_folders)
            # logger.debug('repeated_folders %s'%repeated_folders)
            # if repeated_folders:
            #     print('There are conflicts for some repeated folder names:')
            #     for f in [str(p) for p in repeated_folders]:
            #         print(' [gold1]%s[/gold1]'%f)
            #     print('Here are the complete paths:')
            #     for f in [str(p) for p in complete_path_folders]:
            #         print(' [gold1]%s[/gold1]'%f)
            #     print('please rename and rerun. Quitting..')
            #     sys.exit(1) ####################################################
            return media_grouped_by_folder
        media_grouped_by_folder = _exit_on_folder_name_clash()
        n_CAM_folder = 0
        for folder, list_of_medias_in_folder in media_grouped_by_folder:
            # check all medias are either video or audio recordings in folder
            # if not, warn user and quit.
            dev_types = set([m.device.dev_type for m in list_of_medias_in_folder])
            logger.debug('dev_types for folder%s: %s'%(folder,dev_types))
            if dev_types == {'CAM'}:
                n_CAM_folder += 1
            if len(dev_types) != 1:
                print('\nProblem while scanning for media files. In [gold1]%s[/gold1]:'%folder)
                print('There is a mix of video and audio files:')
                [print('[gold1]%s[/gold1]'%m.path.name, end =', ')
                    for m in list_of_medias_in_folder]
                print('\nplease move them in exclusive folders and rerun.\n')
                sys.exit(1) ######################################################
            unidentified = [m for m in list_of_medias_in_folder
                if m.device.UID == None]
            UIDed = [m for m in list_of_medias_in_folder
                if m.device.UID != None]
            logger.debug('devices in folder %s:'%folder)
            logger.debug('  media with unknown devices %s'%pformat(unidentified))
            logger.debug('  media with UIDed devices %s'%pformat(UIDed))
            if len(unidentified) != 0 and len(UIDed) != 0:
                print('\nProblem while grouping files in [gold1]%s[/gold1]:'%folder)
                print('There is a mix of unidentifiable and identified devices.')
                print('Is this file:')
                for m in unidentified:
                    print(' [gold1]%s[/gold1]'%m.path.name)
                answer = input("In the right folder?")
                if answer.upper() in ["Y", "YES"]:
                    continue
                elif answer.upper() in ["N", "NO"]:
                    # Do action you need
                    print('please move the following files in a folder named appropriately:\n')
                    sys.exit(1) ################################################
            # if, in a folder, there's a mix of different identified devices,
            # Warn user and quit.
            UIDs = [m.device.UID for m in UIDed]
            all_same_device = UIDs.count(UIDs[0]) == len(UIDs)
            logger.debug('UIDs in %s: %s. all_same_device %s'%(folder,
                                        pformat(UIDs), all_same_device))
            if not all_same_device:
                self.input_structure = 'loose'
                # self.top_dir_has_multicam = False
                logger.debug('changed input_structure to loose')
                # device name should be generated (it isn't the folder name...)
                distinct_UIDS = set(UIDs)
                n_UIDs = len(distinct_UIDS)
                logger.debug('There are %i UIDs: %s'%(n_UIDs, distinct_UIDS))
                # Buid CAM01, CAM02 or REC01, REC02.
                # Get dev type from first media in list
                devT = UIDed[0].device.dev_type # 'CAM' or 'REC'
                generic_names = [devT + str(i).zfill(2) for i in range(n_UIDs)]
                devUIDs_names = dict(zip(distinct_UIDS, generic_names))
                logger.debug('devUIDs_names %s'%pformat(devUIDs_names))
                # rename
                for m in UIDed:
                    m.device.name = devUIDs_names[m.device.UID]
                    logger.debug('new name %s'%m.device.name)
            if len(dev_types) != 1:
                print('\nProblem while scanning for media files. In [gold1]%s[/gold1]:'%folder)
                print('There is a mix of files from different devices:')
                [print('[gold1]%s[/gold1]'%m.path.name, end =', ')
                    for m in list_of_medias_in_folder]
                print('\nplease move them in exclusive folders and rerun.\n')
                sys.exit(1) ####################################################
            if len(unidentified) == len(list_of_medias_in_folder):
                # all unidentified
                if len(unidentified) > 1:
                    print('Assuming those files are from the same device:')
                    [print('[gold1]%s[/gold1]'%m.path.name, end =', ')
                        for m in unidentified]
                    print('\nIf not, there\'s a risk of error: put them in exclusive folders and rerun.')
            # if we are here, the check is done: either 
            #   all files in folder are from unidentified device or
            #   all files in folder are from the same identified device
        logger.debug('n_CAM_folder %i'%n_CAM_folder)
        return

    def _parse_track_values(self, tracks_file) -> Tracks:
        """
        read track names for naming separated ISOs
        from tracks_file.

        tokens looked for: mix; mix L; mix R; 0 and TC

        repeating "mic*" pattern signals a stereo track
        and entries will correspondingly panned into
        a stero mix named mixL.wav and mixL.wav

        mic L # spaces are ignored |
        mic R                      | stereo pair
        micB L
        micB R

        Returns: a Tracks instance:
                # track numbers start at 1 for first track (as needed by sox)
                ttc: int # track number of TicTacCode signal
                unused: list # of unused tracks
                stereomics: list # of stereo mics track tuples (Lchan#, Rchan#)
                mix: list # of mixed tracks, if a pair, order is L than R
                others: list #of all other tags: (tag, track#) tuples
                rawtrx: list # list of strings read from file
                error_msg: str # 'None' if none
        e.g.: Tracks(   ttc=2,
                        unused=[],
                        stereomics=[('mic', (4, 3)), ('mic2', (6, 5))],
                        mix=[], others=[('clics', 1)],
                        rawtrx=['clics', 'TC', 'micL', 'micR', 'mic2L;1000', 'mic2R;1000', 'mixL', 'mixR'],
                        error_msg=None, lag_values=[None, None, None, None, '1000', '1000', None, None])
        """
        def _WOspace(chaine):
            ch = [c for c in chaine if c != ' ']
            return ''.join(ch)
        # def _WO_LR(chaine):
        #     ch = [c for c in chaine if c not in 'LR']
        #     return ''.join(ch)
        # def _seemsStereoMic(tag):
        #     # is tag likely a stereo pair tag?
        #     # should starts with 'mic' and ends with 'l' or 'r'
        #     return tag[1:4]=='mic' and tag[0] in 'lr'
        file=open(tracks_file,"r")
        whole_txt = file.read()
        logger.debug('file %s all_lines:\n%s'%(tracks_file, whole_txt))
        tracks_lines_wspaces = [l.split('#')[0] for l in whole_txt.splitlines()
                                        if len(l) > 0 ]
        tracks_lines = [_WOspace(l) for l in tracks_lines_wspaces if len(l) > 0 ]
        rawtrx = [l for l in tracks_lines_wspaces if len(l) > 0 ]
        # add index with tuples, starting at 1
        logger.debug('tracks_lines whole: %s'%tracks_lines)
        def _detach_lag_value(line):
            # look for ";number" ending any line, returns a two-list
            splt = line.split(';')
            if len(splt) == 1:
                splt += [None]
                if len(splt) != 2:
                    # error
                    print('\nText error in %s, line %s has too many ";"'%(
                            tracks_file, line))
            return splt
        tracks_lines, lag_values = zip(*[_detach_lag_value(l) for l 
                                                    in tracks_lines])
        lag_values = [e for e in lag_values] # from tuple to list
        # logger.debug('tracks_lines WO lag: %s'%tracks_lines)
        tracks_lines = [l.lower() for l in tracks_lines]
        logger.debug('tracks_lines lower case: %s'%tracks_lines)
        # print(lag_values)
        logger.debug('lag_values: %s'%lag_values)
        tagsWOl_r = [e[:-1] for e in tracks_lines] # skip last letter
        logger.debug('tags WO LR letter %s'%tagsWOl_r)
        # find idx of start of pairs
        # ['clics', 'TC', 'micL', 'micR', 'mic2L', 'mic2R', 'mixL', 'mixR']
        def _micOrmix(a,b):
            # test if same and mic mic or mix mix
            if len(a) == 0:
                return False
            return (a == b) and (a in 'micmix')
        pair_idx_start =[i for i, same in enumerate([_micOrmix(a,b) for a,b
                        in zip(tagsWOl_r,tagsWOl_r[1:])]) if same]
        logger.debug('pair_idx_start %s'%pair_idx_start)
        def LR_OK(idx):
            # in tracks_lines, check if idx ends a LR pair
            # delays, if any, have been removed
            a = tracks_lines[idx][-1]
            b = tracks_lines[idx+1][-1]
            return a+b in ['lr', 'rl']
        LR_OKs = [LR_OK(p) for p in pair_idx_start]
        logger.debug('LR_OKs %s'%LR_OKs)
        if not all(LR_OKs):
            print('\nError in %s'%tracks_file)
            print('Some tracks are paired but not L and R: %s'%rawtrx)
            print('quitting...')
            quit()
        complete_pairs_idx = pair_idx_start + [i + 1 for i in pair_idx_start]
        singles = set(range(len(tracks_lines))).difference(complete_pairs_idx)
        logger.debug('complete_pairs_idx %s'%complete_pairs_idx)
        logger.debug('singles %s'%singles)
        singles_tag = [tracks_lines[i] for i in singles]
        logger.debug('singles_tag %s'%singles_tag)
        n_tc_token = sum([t == 'tc' for t in singles_tag])
        logger.debug('n tc tags %s'%n_tc_token)
        if n_tc_token == 0:
            print('\nError in %s'%tracks_file)
            print('with %s'%rawtrx)
            print('no TC track found, quitting...')
            quit()
        if n_tc_token > 1:
            print('\nError in %s'%tracks_file)
            print('with %s'%rawtrx)
            print('more than one TC track, quitting...')
            quit()
        output_tracks = Tracks(None,[],[],[],[],rawtrx,None,[])
        output_tracks.ttc = tracks_lines.index('tc') + 1 # 1st = 1
        logger.debug('ttc_chan %s'%output_tracks.ttc)
        zeroed = [i+1 for i, t in enumerate(tracks_lines) if t == '0']
        logger.debug('zeroed %s'%zeroed)
        output_tracks.unused = zeroed
        output_tracks.others = [(st, tracks_lines.index(st)+1) for st
                                in singles_tag if st not
                                in ['tc', 'monomix', '0']]
        logger.debug('output_tracks.others %s'%output_tracks.others)
        # check for monomix
        if 'monomix' in tracks_lines:
            output_tracks.mix = [tracks_lines.index('monomix')+1]
        else:
            output_tracks.mix = []
        # check for stereo mix
        def _findLR(i_first):
            # returns L R indexes (+1 for sox non zero based indexing)
            i_2nd = i_first + 1
            a = tracks_lines[i_first][-1] # l|r at end
            b = tracks_lines[i_2nd][-1] # l|r at end
            if a == 'l':
                if b == 'r':
                    # sequence is mixL mixR
                    return i_first+1, i_2nd+1
                else:
                    print('\nError in %s'%tracks_file)
                    print('with %s'%rawtrx)
                    print('can not find stereo mix')
                    quit()
            elif a == 'r':
                if b == 'l':
                    # sequence is mixR mixL
                    return i_2nd+1, i_first+1
                else:
                    print('\nError in %s'%tracks_file)
                    print('with %s'%rawtrx)
                    print('can not find stereo mix')
                    quit()
        logger.debug('for now, output_tracks.mix %s'%output_tracks.mix)
        mix_pair = [p for p in pair_idx_start if tracks_lines[p][1:] == 'mix']
        if len(mix_pair) == 1:
            # one stereo mix, remove it from other pairs
            i = mix_pair[0]
            LR_pair =  _findLR(i)
            logger.debug('LR_pair %s'%str(LR_pair))
            pair_idx_start.remove(i)
            # consistency check
            if output_tracks.mix != []:
                # already found a mono mix above!
                print('\nError in %s'%tracks_file)
                print('with %s'%rawtrx)
                print('found a mono mix AND a stereo mix')
                quit()
            output_tracks.mix = LR_pair
        logger.debug('finally, output_tracks.mix %s'%str(output_tracks.mix))
        logger.debug('remaining pairs %s'%pair_idx_start)
        # those are stereo pairs
        stereo_pairs = []
        for first_in_pair in pair_idx_start:
            suffix = tracks_lines[first_in_pair][:-1]
            stereo_pairs.append((suffix, _findLR(first_in_pair)))
        logger.debug('stereo_pairs %s'%stereo_pairs)
        output_tracks.stereomics = stereo_pairs
        logger.debug('finished: %s'%output_tracks)
        return output_tracks





