import os, itertools, argparse
from pathlib import Path
from loguru import logger
import sys
from pprint import pformat

logger.level("DEBUG", color="<yellow>")


video_extensions = \
"""webm mkv flv flv vob ogv  ogg drc gif gifv mng avi mov 
qt wmv yuv rm rmvb viv asf  mp4  m4p m4v mpg  mp2  mpeg  mpe 
mpv mpg  mpeg  m2v m4v svi 3gp 3g2 mxf roq nsv""".split() # from wikipedia

def is_video(f):
    # True if name as video extension
    name_ext = f.split('.')
    if len(name_ext) != 2:
        return False
    name, ext = name_ext
    return ext.lower() in video_extensions

def find_ISO_vids_pairs_in_dir(top):
    # look for matching video name and ISO dir name
    # eg: IMG04.mp4 and IMG04_ISO
    # returns list of matches
    # recursively search from 'top' argument
    vids = []
    ISOs = []
    for (root,dirs,files) in os.walk(top, topdown=True):
        for d in dirs:
            if d[-4:] == '_ISO':
                ISOs.append(Path(root)/d)
        for f in files:
            if is_video(f): # add being in SyncedMedia or SyncedMulticamClips folder
                vids.append(Path(root)/f)
    logger.debug('vids %s ISOs %s'%(pformat(vids), pformat(ISOs)))
    matches = []
    for pair in list(itertools.product(vids, ISOs)):
        # print(pair)
        vid, ISO = pair
        vidname, ext = vid.name.split('.')
        if vidname == ISO.name[:-4]:
            matches.append(pair)
        # print(vidname, ISO.name[:-4])
    logger.debug('matches: %s'%pformat(matches))
    return matches

# [print( vid, ISO) for vid, ISO in find_ISO_vids_pairs('.')]

def parse_and_check_arguments():
    # parses directories from command arguments
    # check for consistencies and warn user and exits,
    # if returns, gives:
    #  proxies_dir, originals_dir, audio_dir, both_audio_vid, scan_only
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                    nargs=*,
                    dest='video_dirs',
                    help='Where proxy clips and/or originals are stored')
    parser.add_argument('-a',
                    nargs=1,
                    dest='audio_dir',
                    help='Contains newly changed mix files')
    parser.add_argument('-b',
                    nargs=1,
                    dest='both_audio_vid',
                    help='Directory scanned for both audio and video')
    parser.add_argument('--dry',
                    action='store_true',
                    dest='scan_only',
                    help="Just display changed audio, don't merge")
    args = parser.parse_args()
    logger.debug('args %s'%args)
    # ok cases:
    # -p -o -a + no -b
    # -o -a + no -b
    args_set = [args.proxies_dir != None,
                    args.originals_dir != None,
                    args.audio_dir != None,
                    args.both_audio_vid != None,
                    ]
    p, o, a, b = args_set
    # check that argument -b (both_audio_vid) is used alone
    if b and any([o, a, p]):
        print("\nDon't specify other argument than -b if both audio and video searched in the same directory.\n") 
        parser.print_help(sys.stderr)
        sys.exit(0)
    # check that if proxies (-p) are specified, orginals too (-o)
    if p and not o:
        print("\nIf proxies directory is specified, so should originals directory.\n") 
        parser.print_help(sys.stderr)
        sys.exit(0)
    # check that -o and -a are used together
    if not b and not (o and a):
        print("\nAt least originals and audio directories must be given (-o and -a) when audio and video are in different dir.\n") 
        parser.print_help(sys.stderr)
        sys.exit(0)
    # work in progress (aug 2025), so limit to -b:
    if not b :
        print("\nFor now, only -b argument is supported (a directory scanned for both audio and video) .\n") 
        parser.print_help(sys.stderr)
        sys.exit(0)
    arg_dict = vars(args)
    # list of singletons, so flatten. Keep None and False as is
    return [e[0] if isinstance(e, list) else e for e in arg_dict.values() ]



def main():
    proxies_dir, originals_dir, audio_dir, both_audio_vid, scan_only = \
        parse_and_check_arguments()
    m = find_ISO_vids_pairs_in_dir(both_audio_vid)

if __name__ == '__main__':
    main()
