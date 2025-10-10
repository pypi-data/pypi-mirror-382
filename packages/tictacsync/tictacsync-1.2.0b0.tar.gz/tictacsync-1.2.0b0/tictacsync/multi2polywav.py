import argparse, wave, subprocess, sys
from loguru import logger
from pathlib import Path
from itertools import groupby
import sox, tempfile, os, ffmpeg
from rich import print


"""
this modules can be called from the CLI.
It scans recursively the given folder for multi files wav recordings.
When found, those multifiles are merged in place into a polywav file.
Original multifiles are kept in place but their extension changed from
.wav to .mfw (a reminder for multi file wav)
The name of the newly created polywav file is crafted from the names
of the multi files, eg
4CH002I.wav and 4CH002M.wav gives 4CH002X.wav
"""

MAXSIZEWAV = 1.9 # GB, for suspiciously big wav file


logger.remove()

def print_grby(grby):
    for key, keylist in grby:
        print('\ngrouped by %s:'%key)
        for e in keylist:
            print(' ', e)

def wav_recursive_scan(top_directory):
    files_lower_case = Path(top_directory).rglob('*.wav') 
    files_upper_case = Path(top_directory).rglob('*.WAV')
    files = set(list(files_lower_case) + list(files_upper_case))
    paths = [
        p
        for p in files
        if 'SyncedMedia' not in p.parts
    ]
    return paths

def nframes(path):
    # print(path)
    try:
        with wave.open(str(path), 'rb') as f:
            n_frames = int(f.getnframes())
    except:
        # print('in nframes(), cant open file with wave.open %s'%path)
        try:
            probe = ffmpeg.probe(path)
        except:
            print('cant open with either ffprobe or wave.open%s'%path)
            return 0
        duration_ts = probe['streams'][0]['duration_ts']
        # print(duration_ts)
        return duration_ts
    return n_frames


def build_poly_name(multifiles):
    """
    Returns string of polywav filename, constructed from similitudes between
    multifile names. Ex:
    4CH002I.wav and 4CH002M.wav returns 4CH002X.wav
    """
    s1 = str(multifiles[0].stem)
    s2 = str(multifiles[1].stem)
    if len(s1) != len(s2):
        print('\nCan not build compound name with %s.wav and %s.wav'%(s1,s2))
        print('names lengths differ.')
        print('In folder "%s", quitting.'%multifiles[0].parent)
        sys.exit(1)
    pairs = list(zip(s1, s2))
    not_same = [a for a, b in pairs if a != b ]
    if len(not_same) > 2:
        print('\nCan not build compound name with %s.wav and %s.wav'%(s1,s2))
        print('names differ by more than two characters.')
        print('In folder "%s", quitting.'%multifiles[0].parent)
        sys.exit(1)
    compound = [a if a == b else 'X' for a, b in pairs ]
    return ''.join(compound) + '.wav'

def jump_metadata(from_file, to_file):
    tempfile_for_metadata = tempfile.NamedTemporaryFile(suffix='.wav', delete=True)
    tempfile_for_metadata = tempfile_for_metadata.name
    # ffmpeg -i 32ch-44100-bwf.wav -i onechan.wav -map 1 -map_metadata 0 -c copy outmeta.wav
    process_list = ['ffmpeg', '-loglevel', 'quiet', '-nostats', '-hide_banner', '-i', from_file, '-i', to_file, '-map', '1',
                                     '-map_metadata', '0', '-c', 'copy', tempfile_for_metadata]
    # ss = shlex.split("ffmpeg  -i %s -i %s -map_metadata 0 -c copy %s"%(from_file, to_file, tempfile_for_metadata))
    # print(ss)
    # logger.debug('process %s'%process_list)
    proc = subprocess.run(process_list)
    # os.remove(to_file)
    os.replace(tempfile_for_metadata, to_file)

def build_poly(multifiles):
    # constructs poly name and calls sox
    # multifiles is list of Path
    # change extensions to mfw (multifile wav)
    dir_multi = multifiles[0].parent
    multifiles.reverse()
    poly_name_b = build_poly_name(multifiles) # base only
    poly_name = str(dir_multi/Path(poly_name_b))
    filenames = [str(p) for p in multifiles]
    logger.debug('sox.build args: %s %s'%(
        filenames,
        poly_name))
    cbn = sox.Combiner()
    cbn.set_input_format(file_type=['wav']*len(multifiles))
    status = cbn.build(
        filenames,
        poly_name,
        combine_type='merge')
    logger.debug('sox.build status: %s'%status)
    if status != True:
        print('sox did not merge files')
        sys.exit(1)
    jump_metadata(filenames[0], poly_name)
    print('\nMerging multifiles recordings:', end = ' ')
    [print('[gold1]%s[/gold1]'%p.name, end=' + ') for p in multifiles[:-1]]
    print('[gold1]%s[/gold1]'%multifiles[-1].name, end=' = ')
    print('[gold1]%s[/gold1]'%poly_name_b, end=' ')
    print('(backups will have .MFW as extension)')
    [p.rename(str(p.parent/p.stem) + '.mfw') for p in multifiles]

def getch():
    """Read single character from standard input without echo."""
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def poly_all(top_dir):
    """ 
    Find all multifile recordings and writes polywav files in target folder.
    Multifiles are wav files with the exact same length and whose name differ
    by not more than two characters.
    """
    wavfiles = wav_recursive_scan(top_dir)
    same_dir_key = lambda p: p.parent
    same_length_key = lambda p: nframes(p)
    wavfiles = sorted(wavfiles, key=same_dir_key)
    grouped_by_directory = [ (k, list(iterator)) for k, iterator
            in groupby(wavfiles, same_dir_key)]
    # print("in same dir:")
    # print_grby(grouped_by_directory)
    for key, wavfiles_same_dir in grouped_by_directory:
        # print(wavfiles_same_dir)
        logger.debug('looking into %s for multifiles '%key)
        wavfiles_same_dir = sorted(wavfiles_same_dir, key=nframes)
        grouped_by_length = [ (k, list(iterator)) for k, iterator
            in groupby(wavfiles_same_dir, nframes)]
        # print_grby(grouped_by_length)
        for sample_length, wavfiles_same_length in grouped_by_length:
            # print(wavfiles_same_length)
            if len(wavfiles_same_length) == 1: # no two files same size
                continue
            else:
                size = os.path.getsize(wavfiles_same_length[0])/(2.**30)
                if size < MAXSIZEWAV:
                    build_poly(wavfiles_same_length)
                else:
                    print('Those files have the same size but are big (%0.1fGiB):\n'%size)
                    [print(p.name) for p in wavfiles_same_length]
                    print('\nAre they really simultaneus tracks in multifiles or simply successive chunks')
                    print('of a larger recordings?\n')
                    print('Press c for chunks, m for multifiles: [c or m]', end = "", flush = True)
                    c = ""
                    while c not in ("c", "m"):
                        c = getch().lower()
                    if c == 'm':
                        build_poly(wavfiles_same_length)
                    else:
                        print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "directory",
                type=str,
                nargs='?',
                help="path of media directory",
                default='.'
                )
    args = parser.parse_args()
    # logger.info('arguments: %s'%args)
    logger.debug('args %s'%args)
    poly_all(args.directory)
        # for e in keylist:
        #     print(' ', e)

if __name__ == '__main__':
    main()




