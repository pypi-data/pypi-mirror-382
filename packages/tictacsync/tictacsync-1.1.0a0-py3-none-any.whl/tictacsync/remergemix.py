import argparse, wave, subprocess
from loguru import logger
from pathlib import Path
import sox, tempfile, os, ffmpeg
from rich import print
import shutil, sys, re
from pprint import pformat 
from itertools import groupby

try:
    from . import timeline
except:
    import timeline

DEL_TEMP = False

logger.level("DEBUG", color="<yellow>")
logger.remove()

# logger.add(sys.stdout, filter=lambda r: r["function"] == "_get_ISO_dirs")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "_join_audio2video")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "main")
# logger.add(sys.stdout, filter="__main__")

OUT_DIR = 'SyncedMedia'
SEC_DELAY_CHANGED_ISO = 10 #sec, ISO_DIR changed if diff time is bigger

video_extensions = \
"""webm mkv flv flv vob ogv  ogg drc gif gifv mng avi mov 
qt wmv yuv rm rmvb viv asf  mp4  m4p m4v mpg  mp2  mpeg  mpe 
mpv mpg  mpeg  m2v m4v svi 3gp 3g2 mxf roq nsv""".split() # from wikipedia

def _pathname(tempfile_or_path) -> str:
    # utility for obtaining a str from different filesystem objects
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

def _keep_VIDEO_only(video_path):
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

def _join_audio2video(audio_path: Path, video: Path):
    """
    Replace audio in video (argument)  by the audio contained in
    audio_path (argument) returns nothing
    """
    video_ext = video.name.split('.')[1]
    vid_only_handle = _keep_VIDEO_only(video)
    a_n = _pathname(audio_path)
    v_n = _pathname(vid_only_handle)
    out_n = _pathname(video)
    # building args for debug purpose only:
    ffmpeg_args = (
        ffmpeg
        .input(v_n)
        .output(out_n, vcodec='copy')
        # .output(out_n, shortest=None, vcodec='copy')
        .global_args('-i', a_n, "-hide_banner")
        .overwrite_output()
        .get_args()
    )
    logger.debug('ffmpeg args: %s'%' '.join(ffmpeg_args))
    try: # for real now
        _, out = (
        ffmpeg
        .input(v_n)
        # .output(out_n, shortest=None, vcodec='copy')
        .output(out_n, vcodec='copy')
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

def _changed(dir) -> bool:
    """
    Returns True if any content of dir (arg) is more recent than dir itself by a
    delay of SEC_DELAY_CHANGED_ISO. Uses modification times.
    """
    logger.debug(f'checking {dir.name} for change')
    ISO_modification_time = biggest_mtime_in_dir(dir)
    clip = clip_from_iso(dir)
    clip_mod_time = clip.stat().st_mtime
    # difference of modification time in secs
    ISO_more_recent_by = ISO_modification_time - clip_mod_time
    logger.debug('ISO_more_recent_by: %s'%(ISO_more_recent_by))
    iso_edited = ISO_more_recent_by > SEC_DELAY_CHANGED_ISO
    logger.debug(f'_changed: {iso_edited}')
    return iso_edited

def sox_mix(ISOdir):
    """
    Mixes all wav files present in ISOdir (so excludes ttc file and nullified
    ones).
    Returns a mono or stereo tempfile
    """
    logger.debug(f'mixing {ISOdir}')
    def is_stereo_mic(p):
        re_result = re.match(r'mic([lrLR])*', p.name)
        # logger.debug(f're_result {re_result}')
        return re_result is not None
    stereo_mics = [p for p in ISOdir.iterdir() if is_stereo_mic(p)]
    monofiles = [p for p in ISOdir.iterdir() if p not in stereo_mics]
    # removing ttc files
    def notTTC(p):
        return p.name[:3] != 'ttc'
    monofiles = [p for p in monofiles if notTTC(p)]
    if stereo_mics == []: # mono
        return timeline._sox_mix_files(monofiles) #-----------------------------
    logger.debug(f'stereo_mics: {stereo_mics}')
    def mic(p):
        return re.search(r'(mic\d*)([lrLR])*', p.name).groups()
    mics = [mic(p) for p in stereo_mics]
    p_and_mic = list(zip(stereo_mics, mics))
    logger.debug(f'p_and_mic: {p_and_mic}')
    same_mic_key = lambda pair: pair[1][0]
    p_and_mic = sorted(p_and_mic, key=same_mic_key)
    grouped_by_mic = [ (k, list(iterator)) for k, iterator
            in groupby(p_and_mic, same_mic_key)]
    logger.debug(f'grouped_by_mic: {grouped_by_mic}')
    def order_left_right(groupby_element):
        # returns left and right path for a mic
        name, paths = groupby_element
        def chan(pair):
            # (PosixPath('mic1r_ZOOM.wav'), ('mic1', 'r')) -> 'r'
            return pair[1][1]
        path_n_mic = sorted(paths, key=lambda pair: pair[1][1])
        return [p[0] for p in path_n_mic] # just the path, not  ('mic1', 'r')
    left_right_paths = [order_left_right(e) for e in grouped_by_mic]
    # logger.debug(f'left_right_paths: {left_right_paths}')
    stereo_files = [timeline._sox_combine(pair) for pair in left_right_paths]
    monoNstereo = monofiles + stereo_files
    return timeline._sox_mix_files(monoNstereo)

def get_mix_file(iso_dir):
    """
    If iso_dir (arg) contains a mono mix sound file or a stereo mix, returns its
    path. If not, this creates the mix and returns it. 
    """
    wav_files = list(iso_dir.iterdir())
    logger.debug(f'wav_files {wav_files}')
    def is_mix(p):
        re_result = re.match(r'mix([lrLR])*', p.name)
        # logger.debug(f're_result {re_result}')
        return re_result is not None
    location_mix = [p for p in wav_files if is_mix(p)]
    if location_mix == []:
        logger.debug('no mix track, do the mix')
        return sox_mix(iso_dir)
    else:
        return location_mix

def biggest_mtime_in_dir(folder: Path) -> float:
    # return the most recent mod time of the files in a folder
    dir_content = list(folder.iterdir())
    stats = [p.stat() for p in dir_content]
    mtimes = [stat.st_mtime for stat in stats]
    return max(mtimes)

def clip_from_iso(ISO_dir: Path) -> Path:
    # find the sibling video file of ISO_dir. eg : MVI_01.ISO -> MVI_01.MP4
    folder = ISO_dir.parent
    siblings = list(folder.glob('%s.*'%ISO_dir.stem))
    candidates =[p for p in siblings if p.name.split('.')[1] != 'ISO']
    # should be unique
    if len(candidates) != 1:
        print(f'Error finding video corresponding to {ISO_dir}, quitting')
        sys.exit(1)
    return candidates[0]

def _get_ISO_dirs(top_dir):
    """
    Check if top_dir contains (or somewhere beneath) videos with their
    accompanying ISO folder (like the pair MVI_023.MP4 + MVI_023.ISO). If not
    warns and exits.

    Returns list of paths pointing to ISO dirs.
    """
    p = Path(top_dir)
    ISO_dirs = list(Path(top_dir).rglob('*.ISO'))
    logger.debug('all files: %s'%pformat(ISO_dirs))
    # validation: .ISO should be dir
    all_are_dir = all([p.is_dir() for p in ISO_dirs])
    logger.debug('.ISO are all dir %s'%all_are_dir)
    if not all_are_dir:
        print('Error: some .ISO are not folders??? Quitting. %s'%ISO_dirs)
        sys.exit(1)
    # for each folder check a video file exists with the same stem
    # but with a video format extension (listed in video_extensions)
    for ISO in ISO_dirs:
        logger.debug(f'checking {ISO}')
        voisins = list(ISO.parent.glob(f'{ISO.stem}.*'))
        voisins_suffixes = [p.suffix for p in voisins]
        # remove ISO
        voisins_suffixes.remove('.ISO')
        # validations: should remain one element and should be video
        suffix = voisins_suffixes[0].lower()[1:] # remove dot
        logger.debug(f'remaining ext: {suffix}')
        if len(voisins_suffixes) != 1 or suffix not in video_extensions:
            print(f'Error with {voisins}, no video unique sibling?')
            sys.exit(1) #-------------------------------------------------------
    logger.debug(f'All ok, returning {ISO_dirs}')
    return ISO_dirs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "directory",
                type=str,
                nargs=1,
                help="path of media directory containing Synced videos and their .ISO folder",
                default='.'
                )
    args = parser.parse_args()
    logger.debug('args %s'%args)
    ISO_dirs = _get_ISO_dirs(args.directory[0])
    logger.debug(f'Will check any change in {pformat(ISO_dirs)}')
    changed_ISOs = [isod for isod in ISO_dirs if _changed(isod)]
    logger.debug(f'changed_ISOs: {changed_ISOs}')
    if changed_ISOs != []:
        print('Will remix audio for:')
    for p in changed_ISOs:
        print(p.name)
    newaudio_and_videos = [(get_mix_file(iso), clip_from_iso(iso)) for iso
                                                    in changed_ISOs]
    for audio, video_clip in newaudio_and_videos:
        print(f'Will remerge {video_clip.name}')
        _join_audio2video(audio, video_clip)
    if newaudio_and_videos == []:
        print('Nothing has changed, bye.')
    sys.exit(0)

if __name__ == '__main__':
    main()
