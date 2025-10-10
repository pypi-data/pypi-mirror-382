import argparse, wave, subprocess
from loguru import logger
from pathlib import Path
import sox, tempfile, os, ffmpeg
from rich import print
import shutil


logger.remove()
OUT_DIR = 'SyncedMedia'

def _pathname(tempfile_or_path) -> str:
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

def _join(left_right: list, video: Path, out: Path):
    video_ext = video.name.split('.')[1]
    audio_left = (
        ffmpeg
        .input(_pathname(left_right[0])))
    audio_right = (
        ffmpeg
        .input(_pathname(left_right[1])))
    input_video = ffmpeg.input(_pathname(video))
    out_file = tempfile.NamedTemporaryFile(suffix='.%s'%video_ext)
    try:
        (ffmpeg
        .filter((audio_left, audio_right), 'join', inputs=2,
                    channel_layout='stereo')
        .output(input_video.video, _pathname(out_file),
                    shortest=None, vcodec='copy', loglevel="quiet")
        .overwrite_output()
        .run())
    except ffmpeg.Error as e:
        print(e)
        print(e.stderr.decode('UTF-8'))
        quit()
    shutil.copyfile(_pathname(out_file), _pathname(video))


def sync_cam(dir):
    # dir is a CAM dir, contents are clips and ISO folders
    ISOs = list(dir.glob('*.ISO'))
    for iso in ISOs:
        # iso is a folder
        statResult = iso.stat()
        mtime = statResult.st_mtime
        # print('%s: %s'%(iso.name, biggest_mtime_in_dir(iso)))
        iso_mod_time = biggest_mtime_in_dir(iso)
        clip = clip_from_iso(iso)
        clip_mod_time = clip.stat().st_mtime
        iso_edited = iso_mod_time > clip_mod_time
        # print('clip %s should be resync: %s'%(clip.name, iso_edited))
        # print(clip)
        if iso_edited:
            print('Resyncing [gold1]%s[/gold1]'%clip.name)
            LR_channels = list(valid_audio_files(iso))
            _join(LR_channels, clip, 'test.MOV')


def valid_audio_files(isofolder: Path) -> list:
    """
    Returns two valid audio files to be synced with video
    case A - only two files differing by L and R
    case B - more than two files, two are mixL mixR
    case C - one file only -> quit()
    case D - more than two files, no mixL mixR -> quit()
    """
    files = list(isofolder.iterdir())
    if len(files) == 1: # case C
        print('Error with folder %s: no mixL.wav, mixR.wav'%isofolder)
        print('or micL.wav, micR.wav... Quitting.')
        quit()
    def _is_case_A(files):
        if len(files) != 2:
            return False
        stems = [p.stem.upper() for p in files]
        lasts = [st[-1] for st in stems]
        LR_pair = ''.join(lasts) in ['LR', 'RL']
        prefix = [st[:-1] for st in stems]
        same = prefix[0] == prefix[1]
        return same and LR_pair
    if _is_case_A(files):
        return files
    def _is_case_B(files):
        if len(files) <= 2:
            return False
        stems = [p.stem.upper() for p in files]
        return 'MIXL' in stems and 'MIXR' in stems
    if _is_case_B(files):
        return isofolder.glob('mix?.*')
    print('Error with folder %s: no mixL.wav, mixR.wav'%isofolder)
    print('or micL.wav, micR.wav... Quitting.')
    quit()

def biggest_mtime_in_dir(folder: Path) -> float:
    # return the most recent mod time in a folder
    dir_content = list(folder.iterdir())
    stats = [p.stat() for p in dir_content]
    mtimes = [stat.st_mtime for stat in stats]
    return max(mtimes)

def clip_from_iso(p: Path) -> Path:
    folder = p.parent
    pair = list(folder.glob('%s.*'%p.stem))
    return [p for p in pair if p.name.split('.')[1] != 'ISO'][0]

def synciso(top_dir):
    p = Path(top_dir)/OUT_DIR
    dir_content = list(p.iterdir())
    logger.debug('dir_content %s'%dir_content)
    all_are_dir = all([p.is_dir() for p in dir_content])
    logger.debug('all_are_dir %s'%all_are_dir)
    if not all_are_dir:
        print('Error: resync possible only on structured folders,')
        print('Rerun tictacsync with one directory for each device.')
        quit()
    [sync_cam(f) for f in dir_content]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "directory",
                type=str,
                nargs='+',
                help="path of media directory containing SyncedMedia/",
                default='.'
                )
    args = parser.parse_args()
    # logger.info('arguments: %s'%args)
    logger.debug('args %s'%args)
    synciso(args.directory)
        # for e in keylist:
        #     print(' ', e)

if __name__ == '__main__':
    main()
