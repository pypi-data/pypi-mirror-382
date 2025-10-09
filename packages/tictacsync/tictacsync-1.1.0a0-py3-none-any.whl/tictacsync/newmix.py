import os, itertools, argparse, ffmpeg, tempfile, platformdirs
from pathlib import Path
from loguru import logger
import shutil, sys, re, sox, configparser
from pprint import pformat
from rich import print

try:
    from . import mamconf
except:
    import mamconf


LUA = True
OUT_DIR_DEFAULT = 'SyncedMedia'
MCCDIR = 'SyncedMulticamClips'
SEC_DELAY_CHANGED_SND = 10 #sec, SND_DIR changed if diff time is bigger
DEL_TEMP = True
CONF_FILE = 'mamsync.cfg'

logger.level("DEBUG", color="<yellow>")
logger.remove()
# logger.add(sys.stdout, filter=lambda r: r["function"] == "main")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "find_SND_vids_pairs_in_udir")

DAVINCI_RESOLVE_SCRIPT_LOCATION = '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/'
DAVINCI_RESOLVE_SCRIPT_TEMPLATE = \
"""def ClipWithFilePath(file_path):
    media_pool = app.GetResolve().GetProjectManager().GetCurrentProject().GetMediaPool()
    queue = [media_pool.GetRootFolder()]
    while len(queue) > 0:
        current = queue.pop(0)
        queue += current.GetSubFolderList()
        got_it = [cl for cl in current.GetClipList()
            if cl.GetClipProperty('File Path') == file_path]
        # print(got_it)
        if got_it != []:
            # print('got it')
            return got_it[0]

def findAndReplace(old_file, new_file):
    clip_with_old_file = ClipWithFilePath(old_file)
    if clip_with_old_file == None:
        print(f'did not find clip with path {old_file}')
        sys.exit(0)
    else:
        clip_with_old_file.ReplaceClip(new_file)
    cfp, cn = [clip_with_old_file.GetClipProperty(p) for p in ['File Path', 'Clip Name']]
    if cfp == new_file:
        print(f'Loaded {cn} with a new sound track')
    else:
        print(f'findAndReplace {old_file} -> {new_file} failed')

"""
# python is deprecated... Lua is the way to go

DAVINCI_RESOLVE_SCRIPT_TEMPLATE_LUA = """local function ClipWithPartialPath(partial_path)
    local media_pool = app:GetResolve():GetProjectManager():GetCurrentProject():GetMediaPool()
    local queue = {media_pool:GetRootFolder()}
    while #queue > 0 do
        local current = table.remove(queue, 1)
        local subfolders = current:GetSubFolderList()
        for _, folder in ipairs(subfolders) do
            table.insert(queue, folder)
        end
        local got_it = {}
        local clips = current:GetClipList()
        for _, cl in ipairs(clips) do
            if string.find(cl:GetClipProperty('File Path'), partial_path) then
                table.insert(got_it, cl)
            end
        end
        if #got_it > 0 then
            return got_it[1]
        end
    end
end

local function findAndReplace(old_file, new_file)
    local clip_with_old_file = ClipWithPartialPath(old_file)
    if clip_with_old_file == nil then
        print('did not find clip with path ' .. old_file)
    else
        clip_with_old_file:ReplaceClip(new_file)
        local cfp = clip_with_old_file:GetClipProperty('File Path')
        local cn = clip_with_old_file:GetClipProperty('Clip Name')
        if cfp == new_file then
            print('Loaded ' .. cn .. ' with a new sound track')
        else
            print('findAndReplace ' .. old_file .. ' -> ' .. new_file .. ' failed')
        end
    end
end

local changes = {
"""

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

def is_synced_video(f):
    # True if name as video extension
    # and is under SyncedMedia or SyncedMulticamClips folders
    # f is a Path
    ext = f.suffix[1:] # removing leading '.'
    ok_ext = ext.lower() in video_extensions
    f_parts = f.parts
    ok_folders = OUT_DIR_DEFAULT in f_parts or MCCDIR in f_parts
    # logger.debug('ok_ext: %s ok_folders: %s'%(ok_ext, ok_folders))
    return ok_ext and ok_folders

def find_SND_vids_pairs_in_udir(top):
    # look for matching video name and SND in unique directory
    # in alongside mode (vs MAM mode)
    # eg: IMG04.mp4 and IMG04_SND
    # maybe IMG04v2.mp4 if audio changed before (than it will be IMG04v3.mp4)
    # returns list of (SND, vid) matches
    # recursively search from 'top' argument
    vids = []
    SNDs = []
    for (root,dirs,files) in os.walk(top):
        for d in dirs:
            if d[-4:] == '_SND':
                SNDs.append(Path(root)/d)
        for f in files:
            if is_synced_video(Path(root)/f): # add being in SyncedMedia or SyncedMulticamClips folder
                vids.append(Path(root)/f)
    logger.debug('vids %s SNDs %s'%(pformat(vids), pformat(SNDs)))
    matches = []
    def _names_match(vidname, SND_name):
        # vidname is a str and has no extension
        # vidname could have vNN suffix as in DSC_8064v31 so matches DSC_8064
        if vidname == SND_name: # no suffix presents
            return True
        m = re.match(SND_name + r'v(\d+)', vidname)
        if m != None:
            logger.debug('its a natch and N= %s'%m.groups()[0])
        return m != None
    for pair in list(itertools.product(SNDs, vids)):
        # print(pair)
        SND, vid = pair # Paths
        vidname, ext = vid.name.split('.') # string
        if _names_match(vidname, SND.name[:-4]):
            logger.debug('SND %s matches video %s'%(
                Path('').joinpath(*SND.parts[-2:]),
                Path('').joinpath(*vid.parts[-3:])))
            matches.append(pair) # list of Paths
    logger.debug('matches: %s'%pformat(matches))
    return matches

def find_SND_vids_pairs_in_dual_dir(synced_root, snd_root):
    # look for matching video name and SND in unique directory
    # in alongside mode (vs MAM mode)
    # eg: IMG04.mp4 and directory IMG04_SND
    # maybe IMG04v2.mp4 if audio changed before (than it will be IMG04v3.mp4)
    # returns list of (SND, vid) matches
    # recursively search from 'top' argument
    vids = []
    SNDs = []
    print(f'Will look for new mix in {snd_root} compared to vids in {synced_root}')
    for (root,dirs,files) in os.walk(synced_root):
        for f in files:
            pf = Path(root)/f
            if pf.suffix[1:].lower() in video_extensions:
                if not pf.is_symlink():
                    vids.append(pf)
    for (root,dirs,files) in os.walk(snd_root):
        for d in dirs:
            if d[-4:] == '_SND':
                SNDs.append(Path(root)/d)
    logger.debug('vids %s SNDs %s'%(pformat(vids), pformat(SNDs)))
    matches = []
    def _names_match(vidname, SND_name):
        # vidname is a str and has no extension
        # vidname could have vNN suffix as in DSC_8064v31 so matches DSC_8064
        if vidname == SND_name: # no suffix presents
            return True
        m = re.match(SND_name + r'v(\d+)', vidname)
        if m != None:
            logger.debug('its a natch and N= %s'%m.groups()[0])
        return m != None
    for pair in list(itertools.product(SNDs, vids)):
        # print(pair)
        SND, vid = pair # Paths
        vidname, ext = vid.name.split('.') # string
        if _names_match(vidname, SND.name[:-4]):
            logger.debug('SND %s matches video %s'%(
                Path('').joinpath(*SND.parts[-2:]),
                Path('').joinpath(*vid.parts[-3:])))
            matches.append(pair) # list of Paths
    logger.debug('matches: %s'%pformat(matches))
    return matches

def parse_and_check_arguments():
    # parses directories from command arguments
    # check for consistencies and warn user and exits,
    # returns parser.parse_args()
    parser = argparse.ArgumentParser()
    parser.add_argument('-u',
                    nargs=1,
                    dest='unique_directory',
                    help='Directory scanned for both audio and video, when tictacsync is used rather than mamsync.')
    parser.add_argument('--dry',
                    action='store_true',
                    dest='scan_only',
                    help="Just display changed audio, don't merge")
    args = parser.parse_args()
    logger.debug('args %s'%args)
    if args.scan_only:
        print('Sorry, --dry option not implemented yet, bye.')
        sys.exit(0)
    return args

def get_recent_mix(SND_dir, vid):
    # check if there are mixl, mixr or mix files in SND_dir
    # and return the paths if they are more recent than vid.
    # returns empty tuple otherwise
    # arguments SND_dir, vid and returned values are of Path type
    wav_files = list(SND_dir.iterdir())
    logger.debug(f'wav_files {wav_files} in {SND_dir}')
    def is_mix(p):
        re_result = re.match(r'mix([lrLR])*', p.name)
        logger.debug(f'for {p.name} re_result looking for mix {re_result}')
        return re_result is not None
    mix_files = [p for p in wav_files if is_mix(p)]
    if len(mix_files) == 0:
        return ()
    # consistency check, should be 1 or 2 files
    if not len(mix_files) in (1,2):
        print(f'\nError: too many mix files in [bold]{SND_dir}[/bold], bye.')
        sys.exit(0)
    # one file? it must be mix.wav
    if len(mix_files) == 1:
        fn = mix_files[0].name
        if fn.upper() != 'MIX.WAV':
            print(f'\nError in [bold]{SND_dir}[/bold], the only file should be mix.wav, not [bold]{fn}[/bold][/bold]; bye.')
            sys.exit(0)
    # two files? verify they are mixL and mixR and mono each
    if len(mix_files) == 2:
        first3uppercase = [p.name[:4].upper() for p in mix_files]
        first3uppercase.sort()
        first3uppercase = ''.join(first3uppercase)
        if first3uppercase != 'MIXLMIXR':
            print(f'\nError: mix names mismatch in [bold]{SND_dir}[/bold];')
            print(f'names are [bold]{[p.name for p in mix_files]}[/bold], check they are simply mixL.wav and mixR.wav; bye.')
            sys.exit(0)
        def _nch(p):
            return sox.file_info.channels(str(p))
        are_mono = [_nch(p) == 1 for p in mix_files]
        logger.debug('are_mono: %s'%are_mono)
        if not all(are_mono):
            print(f'\nError in [bold]{SND_dir}[/bold], some files are not mono, bye.')
            sys.exit(0)
    logger.debug(f'mix_files: {mix_files}')
    # check dates, if two files, take first
    mix_modification_time = mix_files[0].stat().st_mtime
    vid_mod_time = vid.stat().st_mtime
    # difference of modification time in secs
    mix_more_recent_by = mix_modification_time - vid_mod_time
    logger.debug('mix_more_recent_by: %s'%mix_more_recent_by)
    if mix_more_recent_by > SEC_DELAY_CHANGED_SND:
        if len(mix_files) == 1:
            two_folders_up = mix_files[0]
            # two_folders_up = Path('').joinpath(*mix_files[0].parts[-3:])
            print(f'\nFound new mix: [bold]{two_folders_up}[/bold]')
        return mix_files
    else:
        return ()

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

def _change_audio4video(audio_path: Path, video: Path):
    """
    Replace audio in video (argument)  by the audio contained in
    audio_path (argument) returns nothing
    If name has version number, bump it (DSC_8064v13.MOV -> DSC_8064v14.MOV)
    Returns string tuple of old and new video files
    old file in incomplete e.g.: ../DSC_8064  without version and ext
    new file is complete

    """
    vidname, video_ext = video.name.split('.')
    vid_only_handle = _keep_VIDEO_only(video)
    a_n = _pathname(audio_path)
    v_n = _pathname(vid_only_handle)
    # check v suffix
    m = re.match(f'(.*)v(\\d+)', vidname)
    if m == None:
        # no suffix, add one
        out_path = video.parent / f'{vidname}v2.{video_ext}'
        out_n = _pathname(out_path)
        # for Resolve search
        partial_filename = str(video.parent / vidname)
    else:
        base, number_str = m.groups()
        logger.debug(f'base {base}, number_str {number_str}')
        up_tick =  1 + int(number_str)
        out_path = video.parent / f'{base}v{up_tick}.{video_ext}'
        out_n = _pathname(out_path)
        # for Resolve search
        partial_filename = str(video.parent / base)
    print(f'Video [bold]{video}[/bold] \nhas new sound and is now [bold]{out_path}[/bold]')
    logger.debug(f'partial filname {partial_filename}')
    old_file = str(video)
    new_file = str(out_path)
    # video.unlink() # remove old one
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
    return partial_filename, new_file

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

def generate_script(new_mixes):
    if LUA:
        script = DAVINCI_RESOLVE_SCRIPT_TEMPLATE_LUA
        postlude = ''
        for a,b in new_mixes:
            postlude += '{"%s","%s"},\n'%(a,b)
            # postlude += f"('{a}','{b}'),\n"
        postlude += '}\n\nfor _, pair in ipairs(changes) do\n'
        postlude += '    findAndReplace(pair[1], pair[2])\n'
        postlude += '    os.remove(pair[1])\n'
        postlude += 'end\n'
        # postlude += 'os.remove(pair[1])\n'
    else: # python
        script = DAVINCI_RESOLVE_SCRIPT_TEMPLATE
        postlude = '\nchanges = [\n'
        for a,b in new_mixes:
            postlude += '("%s","%s"),\n'%(a,b)
        postlude += ']\n'
        postlude += '[findAndReplace(a,b) for a, b in changes]\n\n'
    # foo = '[findAndReplace(a,b) for a, b in changes\n'
    # print('foo',foo)
    # print(postlude + foo)
    return script + postlude

def main():
    # proxies_dir, originals_dir, audio_dir, unique_directory, scan_only = \
    #     parse_and_check_arguments()
    args = parse_and_check_arguments()
    if args.unique_directory != None:
        # alongside
        matching_pairs = find_SND_vids_pairs_in_udir(args.unique_directory[0])
    else:
        # MAM mode
        raw_root, synced_root, snd_root, proxies = mamconf.get_proj(False)
        if raw_root == None:
            print('Error: without -u option, mamsync should be configured before using newmix')
            sys.exit(0)
        matching_pairs = find_SND_vids_pairs_in_dual_dir(synced_root, snd_root)
        logger.debug(f'matching_pairs {pformat(matching_pairs)}')
    changes = []
    for SND_dir, vid in matching_pairs:
        new_mix_files = get_recent_mix(SND_dir, vid)
        logger.debug('new_mix_files: %s'%str(new_mix_files))
        if new_mix_files != ():
            logger.debug(f'new mixes {new_mix_files} in {SND_dir} for {vid.name}')
            if len(new_mix_files) == 2:
                new_audio_wav = _sox_combine(new_mix_files)
                logger.debug('stereo_wav: %s'%new_audio_wav)
            else: # len == 1, mono wav file
                new_audio_wav = new_mix_files[0]
            old_file, new_file = _change_audio4video(new_audio_wav, vid)
            changes.append((old_file, new_file))
    if len(changes) == 0:
        print('No new mix.')
        sys.exit(0)
    logger.debug(f'changes {pformat(changes)}')
    script = generate_script(changes)
    fist_vid, _ = changes[0]
    fist_name = Path(fist_vid).name
    title = f'New sound for {fist_name}'
    new_sound_clips = [p for p in Path(DAVINCI_RESOLVE_SCRIPT_LOCATION).iterdir() if 'New sound for' in str(p)]
    if len(new_sound_clips) != 0:
        print('There is already some "New sound for" Resolve scripts')
        for p in new_sound_clips:
            print(p)
        while ( res:=input("Is it OK to delete them? (you could also do it manually). Enter y/n: ").lower() ) not in {"y", "n"}: pass
        if res == 'y':
             [p.unlink() for p in new_sound_clips]
    # title = str(fist_vid)
    if len(changes) > 1:
        title += ' and others'
    if LUA:        
        script_path = Path(DAVINCI_RESOLVE_SCRIPT_LOCATION)/f'{title}.lua'
        script += f'os.remove("{script_path}")\n'
    else: 
        # python version is deprecated...
        script_path = Path(DAVINCI_RESOLVE_SCRIPT_LOCATION)/f'{title}.py'
    with open(script_path, 'w') as fh:
        fh.write(script)
    print(f'Wrote script {script_path}')
    # print(script)


if __name__ == '__main__':
    main()    
