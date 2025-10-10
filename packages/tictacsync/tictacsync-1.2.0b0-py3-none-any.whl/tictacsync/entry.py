
# I know, the following is ugly, but I need those try's to
# run the command in my dev setting AND from
# a deployment set-up... surely I'm setting
# things wrong [TODO]: find why and clean up this mess

try:
    from . import yaltc
    from . import device_scanner
    from . import timeline
    from . import multi2polywav
except:
    import yaltc
    import device_scanner
    import timeline
    import multi2polywav

import argparse, tempfile, configparser
from loguru import logger
from pathlib import Path
# import os, sys
import os, sys, sox, platformdirs
from rich.progress import track
# from pprint import pprint
from rich.console import Console
# from rich.text import Text
from rich.table import Table
from rich import print
from pprint import pprint, pformat
import numpy as np

DEL_TEMP = False

av_file_extensions = \
"""MOV webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp aa aac aax act aiff alac
amr ape au awb dss dvf flac gsm iklax ivs m4a m4b m4p mmf mp3 mpc msv nmf
ogg oga mogg opus ra rm raw rf64 sln tta voc vox wav wma wv webm 8svx cda""".split()

logger.level("DEBUG", color="<yellow>")

def process_single(file, args):
    # argument is a single file
    m = device_scanner.media_at_path(None, Path(file))
    if args.plotting:
        print('\nPlots can be zoomed and panned...')
        print('Close window for next one.')
    a_rec = yaltc.Recording(m, do_plots=args.plotting)
    time = a_rec.get_start_time()
    # time = a_rec.get_start_time(plots=args.plotting)
    if time != None:
        frac_time = int(time.microsecond / 1e2)
        d = '%s.%s'%(time.strftime("%Y-%m-%d %H:%M:%S"),frac_time)
        if args.terse:
            print('%s UTC:%s pulse: %i in chan %i'%(file, d, a_rec.sync_position,
                        a_rec.TicTacCode_channel))
        else:
            print('\nRecording started at [gold1]%s[/gold1] UTC'%d)
            print('true sample rate: [gold1]%.3f Hz[/gold1]'%a_rec.true_samplerate)
            print('first sync at [gold1]%i[/gold1] samples in channel %i'%(a_rec.sync_position,
                        a_rec.TicTacCode_channel))
            print('N.B.: all results are precise to the displayed digits!\n')
    else:
        if args.terse:
            print('%s UTC: None'%(file))
        else:
            print('Start time couldnt be determined')
    sys.exit(1)

def process_lag_adjustement(media_object):
    # trim channels that are lagging (as stated in tracks.txt)
    # replace the old file, and rename the old one with .wavbk
    # if .wavbk exist, process was done already, so dont process
    # returns nothing
    lags = media_object.device.tracks.lag_values
    logger.debug('will process %s lags'%[lags])
    channels = timeline._sox_split_channels(media_object.path)
    # add bk to file on filesystem, but media_object.path is unchanged (?)
    backup_name = str(media_object.path) + 'bk'
    if Path(backup_name).exists():
        logger.debug('%s exists, so return now.'%backup_name)
        return
    media_object.path.replace(backup_name)
    logger.debug('channels %s'%channels)
    def _trim(lag, chan_file):
        # for lag
        if lag == None:
            return chan_file
        else:
            logger.debug('process %s for lag of %s'%(chan_file, lag))            
            sox_transform = sox.Transformer()
            sox_transform.trim(float(lag)*1e-3)
            output_fh = tempfile.NamedTemporaryFile(suffix='.wav', delete=DEL_TEMP)
            out_file = timeline._pathname(output_fh)
            input_file = timeline._pathname(chan_file)
            logger.debug('sox in and out files: %s %s'%(input_file, out_file))
            logger.debug('calling sox_transform.build()')
            status = sox_transform.build(input_file, out_file, return_output=True )
            logger.debug('sox.build exit code %s'%str(status))
        return output_fh
    new_channels = [_trim(*e) for e in zip(lags, channels)]
    logger.debug('new_channels %s'%new_channels)
    trimmed_multichanfile = timeline._sox_combine(new_channels)
    logger.debug('trimmed_multichanfile %s'%timeline._pathname(trimmed_multichanfile))
    Path(timeline._pathname(trimmed_multichanfile)).replace(media_object.path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "path",
                type=str,
                nargs='*',
                help="directory_name or media_file"
                )
    # parser.add_argument("directory", nargs="?", help="path of media directory")
    # parser.add_argument('-v', action='store_true')
    parser.add_argument('-v',
                        action='store_true',  #ie default False
                        dest='verbose_output',
                        help='Set verbose ouput')
    # parser.add_argument('--stop_mirroring',
    #                     action='store_true',  #ie default False
    #                     dest='stop_mirroring',
    #                     help='Stop mirroring mode, will write synced files alongside originals.')
    # parser.add_argument('--start-project', '-s' ,
    #                 nargs=2,
    #                 dest='proj_folders',
    #                 default = [],
    #                 help='start mirrored tree output mode and specifies 2 folders: source (RAW) and destination (synced).')
    parser.add_argument('-t','--timelineoffset',
                    nargs=1,
                    default=['00:00:00:00'],
                    dest='timelineoffset',
                    help='When processing multicam, where to place clips on NLE timeline (HH:MM:SS:FF)')
    parser.add_argument('-p',
                    action='store_true',
                    dest='plotting',
                    help='Produce plots')
    parser.add_argument('-d',
                    action='store_true',
                    dest='dont_write_cam_folder',
                    help="Even if originals are inside CAM folders, don't put synced clips inside a CAM identified folder")
    # parser.add_argument('-m',
    #                 action='store_true',
    #                 dest='multicam',
    #                 help='Outputs multicam structure for NLE program (based on Davinci Resolve input processing)')
    parser.add_argument('--isos',
                    action='store_true',
                    dest='write_ISOs',
                    help='Cut ISO sound files')
    parser.add_argument('--nosync',
                    action='store_true',
                    dest='nosync',
                    help='Just scan and decode')
    parser.add_argument('--terse',
                    action='store_true',
                    dest='terse',
                    help='Terse output')
    args = parser.parse_args()
    # print(args)
    if len(args.timelineoffset) != 1:
        print('--timelineoffset needs one value, got %s'%args.timelineoffset)
        quit()
    if args.verbose_output:
        logger.add(sys.stderr, level="DEBUG")

    # logger.add(sys.stdout, filter=lambda r: r["function"] == "_write_ISOs")
    logger.add(sys.stdout, filter=lambda r: r["function"] == "_build_and_write_audio")
    #
    # logger.add(sys.stdout, filter="__main__")
    # logger.add(sys.stdout, filter="yaltc")

    # logger.add(sys.stdout, filter=lambda r: r["function"] == "move_multicam_to_dir")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "_dev_type_for_name")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "scan_media_and_build_devices_UID")

    top_dir = args.path[0]
    if os.path.isfile(top_dir):
        file = top_dir
        process_single(file, args)
    if not os.path.isdir(top_dir):
        print('%s is not a directory or doesnt exist.'%top_dir)
        sys.exit(1)
    multi2polywav.poly_all(top_dir)
    scanner = device_scanner.Scanner(top_dir, stay_silent=args.terse)
    scanner.scan_media_and_build_devices_UID()
    for m in scanner.found_media_files:
        if m.device.tracks:
            if not all([lv == None for lv in m.device.tracks.lag_values]):
                logger.debug('%s has lag_values %s'%(
                        m.path, m.device.tracks.lag_values))
                # any lag for a channel is specified by user in tracks.txt
                process_lag_adjustement(m)
    audio_REC_only = all([m.device.dev_type == 'REC' for m
                                        in scanner.found_media_files])
    if audio_REC_only:
        if scanner.input_structure != 'ordered':
            print('For merging audio only, use a directory per device, quitting')
            sys.exit(1)
        print('\n\n\nOnly audio recordings are present')
        print('Which device should be the reference?\n')
        devices = scanner.get_devices()
        maxch = len(devices)
        for i, d in enumerate(devices):
            print('\t%i - %s'%(i+1, d.name))
        ref_device = list(devices)[3 - 1]
        print('When only audio recordings are present, ISOs files will be cut and written.')
    if not args.terse:
        if scanner.input_structure == 'ordered':
            print('\nDetected structured folders')
            # if scanner.top_dir_has_multicam:
            #     print(', multicam')
            # else:
            #     print()
        else:
            print('\nDetected loose structure')
            if scanner.CAM_numbers() > 1:
                print('\nNote: different CAMs are present, will sync audio for each of them but if you want to set their')
                print('respective timecode for NLE timeline alignement you should regroup clips by CAM under their own DIR.')
        print('\nFound [gold1]%i[/gold1] media files '%(
            len(scanner.found_media_files)), end='')
        print('from [gold1]%i[/gold1] devices:\n'%(
            scanner.get_devices_number()))
        all_devices = scanner.get_devices()
        for dev in all_devices:
            dt = 'Camera' if dev.dev_type == 'CAM' else 'Recorder'
            print('%s [gold1]%s[/gold1] with files:'%(dt, dev.name), end = ' ')
            medias = scanner.get_media_for_device(dev)
            for m in medias[:-1]: # last printed out of loop
                print('[gold1]%s[/gold1]'%m.path.name, end=', ')
            print('[gold1]%s[/gold1]'%medias[-1].path.name)
            a_media = medias[0]
        # check if all audio recorders have same sampling freq
        freqs = [dev.sampling_freq for dev in all_devices if dev.dev_type == 'REC']
        same = np.isclose(np.std(freqs),0)
        logger.debug('sampling freqs from audio recorders %s, same:%s'%(freqs, same))
        if not same:
            print('some audio recorders have different sampling frequencies:')
            print(freqs)
            print('resulting in undefined results: quitting...')
            quit()
        print()
    # recordings, rec_with_TTC = process_files(scanner.found_media_files, args)
    recordings = [yaltc.Recording(m, do_plots=args.plotting) for m 
                                            in scanner.found_media_files]
    recordings_with_time =  [
        rec 
        for rec in recordings
        if rec.get_start_time()
        ]
    if audio_REC_only:
        for rec in recordings:
        # print(rec, rec.device == ref_device)
            if rec.device == ref_device:
                rec.is_audio_reference = True
    if not args.terse:    
        table = Table(title="tictacsync results")
        table.add_column("Recording\n", justify="center", style='gold1')
        table.add_column("TTC chan\n (1st=#0)", justify="center", style='gold1')
        # table.add_column("Device\n", justify="center", style='gold1')
        table.add_column("UTC times\nstart:end", justify="center", style='gold1')
        table.add_column("Clock drift\n(ppm)", justify="right", style='gold1')
        # table.add_column("SN ratio\n(dB)", justify="center", style='gold1')
        table.add_column("Date\n", justify="center", style='gold1')
        rec_WO_time = [
            rec.AVpath.name
            for rec in recordings
            if rec not in recordings_with_time]
        if rec_WO_time:
            print('No time found for: ',end='')
            [print(rec, end=' ') for rec in rec_WO_time]
            print('\n')
        for r in recordings_with_time:
            date = r.get_start_time().strftime("%y-%m-%d")
            start_HHMMSS = r.get_start_time().strftime("%Hh%Mm%Ss")
            end_MMSS = r.get_end_time().strftime("%Mm%Ss")
            times_range = start_HHMMSS + ':' + end_MMSS
            table.add_row(
                str(r.AVpath.name),
                str(r.TicTacCode_channel),
                # r.device,
                times_range,
                # '%.6f'%(r.true_samplerate/1e3),
                '%2i'%(r.get_samplerate_drift()),
                # '%.0f'%r.decoder.SN_ratio,
                date
                )
        console = Console()
        console.print(table)
        print()
    n_devices = scanner.get_devices_number()
    if len(recordings_with_time) < 2:
        if not args.terse:
            print('\nNothing to sync, exiting.\n')
        sys.exit(1)
    matcher = timeline.Matcher(recordings_with_time)
    matcher.scan_audio_for_each_videoclip()
    if not matcher.mergers:
        if not args.terse:
            print('\nNothing to sync, bye.\n')
        sys.exit(1)
    asked_ISOs = args.write_ISOs
    if asked_ISOs and scanner.input_structure != 'ordered':
        print('Warning, can\'t write ISOs without structured folders: [gold1]--isos[/gold1] option ignored.\n')
        asked_ISOs = False
    # output_dir = args.o
    # if args.verbose_output or args.terse: # verbose, so no progress bars
    print('Merging...')
    # for merger in matcher.mergers:
    #     merger.build_audio_and_write_merged_media(top_dir,
    #     args.dont_write_cam_folder,
    #     asked_ISOs,
    #     audio_REC_only)
    for merger in matcher.mergers:
        if audio_REC_only:
            # rare
            merger._build_and_write_audio(top_dir)
        else:
            # almost always syncing audio to video clips
            merger._build_audio_and_write_video(top_dir,
                args.dont_write_cam_folder, asked_ISOs)
    if not args.terse:
        print("\n")
    # find out where files were written
    # a_merger = matcher.mergers[0]
    for merger in matcher.mergers:
        print('[gold1]%s[/gold1]'%merger.videoclip.AVpath.name, end='')
        for audio in merger.get_matched_audio_recs():
            print(' + [gold1]%s[/gold1]'%audio.AVpath.name, end='')
        new_file = merger.videoclip.final_synced_file.parts
        final_p = merger.videoclip.final_synced_file
        nameAnd2Parents = Path('').joinpath(*final_p.parts[-2:])
        print(' became [gold1]%s[/gold1]'%nameAnd2Parents)
        # matcher._build_otio_tracks_for_cam()
    if not audio_REC_only:        
        matcher.set_up_clusters() # multicam
        matcher.shrink_gaps_between_takes(args.timelineoffset)
        logger.debug('matcher.multicam_clips_clusters %s'%
                            pformat(matcher.multicam_clips_clusters))
        # clusters is list of {'end': t1, 'start': t2, 'vids': [r1,r3]}
        # really_clusters is True if one of them has len() > 1
        really_clusters = any([len(cl['vids']) > 1 for cl
                            in matcher.multicam_clips_clusters])
        if really_clusters:
            if scanner.input_structure == 'loose':
                print('\nThere are synced multicam clips but without structured folders')
                print('they were not grouped together under the same folder.')
            else:
                matcher.move_multicam_to_dir()
        else:
            logger.debug('not really a multicam cluster, nothing to move')
        sys.exit(0)
    
if __name__ == '__main__':
    main()



