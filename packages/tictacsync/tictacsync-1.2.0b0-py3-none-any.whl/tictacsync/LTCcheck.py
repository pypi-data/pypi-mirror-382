print('Loading modules')
import subprocess, io
import argparse, os, sys, ffmpeg
from loguru import logger
from pathlib import Path
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from rich.progress import track, Progress
from pprint import pprint
from collections import deque
import wave
try:
    from . import yaltc
except:
    import yaltc
try:
    from . import device_scanner
except:
    import device_scanner

# LEVELMODE = 'over_noise_silence'
LEVELMODE = 'mean_silence_AFSK'

OFFSET_NXT_PULSE = 50 # samples
LENGTH_EXTRACT = int(14e-3 * 96000) # samples max freq

logger.level("DEBUG", color="<yellow>")
logger.remove()
# logger.add(sys.stdout, filter="tictacsync.LTCcheck")
# logger.add(sys.stdout, filter="tictacsync.yaltc")

def ppm(a,b):
    return 1e6*(max(a,b)/min(a,b)-1)

class TCframe:
    def __init__(self, string, max_FF):
        # string is 'HH:MM:SS:FF' or ;|,|.
        # max_FF is int for max frame number (hence fps-1)
        string = string.replace('.',':').replace(';',':').replace(',',':')
        ints = [int(e) for e in string.split(':')]
        self.HH = ints[0]
        self.MM = ints[1]
        self.SS = ints[2]
        self.FF = ints[3]
        self.MAXFF = max_FF

    def __repr__(self):
        # return '%s-%s-%s-%s/%i'%(*self.ints(), self.MAXFF)
        return '%02i-%02i-%02i-%02i'%self.ints()

    def ints(self):
        return (self.HH,self.MM,self.SS,self.FF)

    def __eq__(self, other):
        a,b,c,d = self.ints()
        h,m,s,f = other.ints()
        return a==h and b==m and c==s and d==f

    def __sub__(self, tcf2):
        # H1, M1, S1, F1 = self.ints()
        # H2, M2, S2, F2 = tcf2.ints()
        f1 = np.array(self.ints())
        f2 = np.array(tcf2.ints())
        HR, MR, SR, FR = f1 - f2
        if FR < 0:
            FR += self.MAXFF + 1
            SR -= 1 # borrow
        if SR < 0:
            SR += 60
            MR -= 1 # borrow
        if MR < 0:
            MR += 60
            HR -= 1 # borrow
        if HR < 0:
            HR += 24 # underflow?
        # logger.debug('%s %s'%(self.ints(), tcf2.ints()))
        return TCframe('%02i:%02i:%02i:%02i'%(HR,MR,SR,FR), self.MAXFF)

def read_whole_audio_data(path):
    dryrun = (ffmpeg
        .input(str(path))
        .output('pipe:', format='s16le', acodec='pcm_s16le')
        .get_args())
    dryrun = ' '.join(dryrun)
    logger.debug('using ffmpeg-python built args to pipe wav file into numpy array:\nffmpeg %s'%dryrun)
    try:
        out, _ = (ffmpeg
            .input(str(path))
            .output('pipe:', format='s16le', acodec='pcm_s16le')
            .global_args("-loglevel", "quiet")
            .global_args("-nostats")
            .global_args("-hide_banner")
            .run(capture_stdout=True))
        data = np.frombuffer(out, np.int16)
    except ffmpeg.Error as e:
        print('error',e.stderr)
    with wave.open(path, 'rb') as f:
        samplerate = f.getframerate()
        n_chan = f.getnchannels()
    all_channels_data = data.reshape(int(len(data)/n_chan),n_chan).T
    return all_channels_data   

def find_nearest_fps(value):
    array = np.asarray([24, 25, 30])
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def fps_rel_to_audio(frame_pos, samplerate):
    _, first_frame_pos = frame_pos[0]
    _, scnd_last_frame_pos = frame_pos[-2]
    frame_duration = (scnd_last_frame_pos - first_frame_pos)/len(frame_pos[:-2]) # in audio samples
    fps = float(samplerate) / frame_duration
    return fps

# def HHMMSSFF_from_line(line):
#   line = line.replace('.',':')
#   line = line.replace(';',':')
#   ll = line.split()[1].split(':')
#   return [int(e) for e in ll]

def check_continuity_and_DF(LTC_frames_and_pos):
    errors = []
    DF_flag = False
    oneframe = TCframe('00:00:00:01',None)
    threeframes = TCframe('00:00:00:03',None)
    last_two_TC = deque([], maxlen=2)
    last_two_TC.append(LTC_frames_and_pos[0][0])
    last_two_TC.append(LTC_frames_and_pos[1][0])
    for frame, pos in track(LTC_frames_and_pos[2:],
            description="Checking each frame increment"):
        last_two_TC.append(frame)
        past, now = last_two_TC
        diff = now - past
        if diff not in [oneframe, threeframes]:
            errors.append((frame, pos))
            continue
        if diff == oneframe:
            continue
        if diff == threeframes: 
            # DF? check if it is 59:xx and minutes are not mult. of tens
            if past.SS != 59 or now.MM%10 == 0: 
                errors.append((frame, pos))
            DF_flag = True
    return errors, DF_flag

def ltcdump_and_check(file, channel):
    # returns list of anormal frames, a bool if TC is DF, fps and
    # a list of tuples (frame => str, sample position in file => int) as
    # determined by external util ltcdump https://github.com/x42/ltc-tools
    process_list = ["ltcdump","-c %i"%channel, file]
    logger.debug('process %s'%process_list)
    proc = subprocess.Popen(process_list, stdout=subprocess.PIPE)
    LTC_frames_and_pos = []
    iter_io = io.TextIOWrapper(proc.stdout, encoding="utf-8")
    next(iter_io) # ltcdump 1st line: User bits  Timecode   |    Pos. (samples)
    print()
    try:
        next(iter_io) # ltcdump 2nd line: #DISCONTINUITY
    except StopIteration:
        print('ltcdump has no output, is channel #%i really LTC?'%channel)
        quit()
    old = 0
    for line in track(iter_io,
        description='       Parsing ltcdump output'):  # next ones
        # print(line)
        if line == '#DISCONTINUITY\n':
            # print('#DISCONTINUITY!')
            continue
        user_bits, HHMMSSFF_str, _, start_sample, end_sample =\
                line.split()
        audio_position = int(end_sample)
        # print(audio_position - old, end=' ')
        # old = audio_position
        # audio_position = int(start_sample)
        tc = HHMMSSFF_str
        LTC_frames_and_pos.append((tc, audio_position))
    with wave.open(file, 'rb') as f:
        samplerate = f.getframerate()
    fps = fps_rel_to_audio(LTC_frames_and_pos, samplerate)
    rounded_fps = round(fps)
    LTC_frames_and_pos = [(TCframe(tc, rounded_fps-1), pos) for tc, pos in LTC_frames_and_pos]
    errors, DF_flag = check_continuity_and_DF(LTC_frames_and_pos)
    return errors, DF_flag, fps, LTC_frames_and_pos

def find_pulses(TTC_data, recording):
    samplerate = recording.true_samplerate
    i_samplerate = round(samplerate)
    pulse_position = recording.sync_position
    logger.debug('first detected pulse %i'%pulse_position)
    # first_pulse_nbr_of_seconds = int(pulse_position/samplerate)
    # if first_pulse_nbr_of_seconds > 1:
    #     pulse_position = pulse_position%i_samplerate # very first pulse in file
    # print('0 %i'%pulse_position)
    pulse_position = pulse_position%i_samplerate
    logger.debug('starting at %i'%pulse_position)
    second = 0
    duration = int(recording.get_duration())
    decoder = recording.decoder
    pulse_detection_level = decoder._get_pulse_detection_level()
    logger.debug(' detection level %f'%pulse_detection_level)
    pulses = []
    approx_next_pulse = pulse_position
    skipped_printed = False
    while second < duration - 1:
        second += 1
        approx_next_pulse -= OFFSET_NXT_PULSE
        start_of_extract = approx_next_pulse
        sound_extract = TTC_data[start_of_extract:start_of_extract + LENGTH_EXTRACT]
        abs_signal = abs(sound_extract)
        detected_point = \
                np.argmax(abs_signal > pulse_detection_level)
        old_pulse_position = pulse_position
        pulse_position = detected_point + start_of_extract
        diff = pulse_position - old_pulse_position
        logger.debug('pulse_position %f old_pulse_position %f diff %f'%(pulse_position,
                        old_pulse_position, diff))
        if not np.isclose(diff, samplerate, rtol=1e-4):
            if not skipped_printed:
                print('\nSkipped: ', end='')
                skipped_printed = True
            print('%i, '%(pulse_position), end='')
            # if diff < samplerate:
            # else:
                # print('skipped: samples %i and %i are too far'%(pulse_position, old_pulse_position))
        else:          
            pulses.append((second, pulse_position))
        approx_next_pulse = pulse_position + i_samplerate
    if skipped_printed:
        print('\n')
    return pulses

def main():
    print('in main()')
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "LTC_chan",
                type=int,
                # nargs=2,
                help="LTC channel number"
                )
    parser.add_argument(
                "file_argument",
                type=str,
                nargs=1,
                help="media file"
                )
    args = parser.parse_args()
    # print(args.channels)
    LTC_chan = args.LTC_chan
    file_argument = args.file_argument[0]
    logger.info('args.file_argument: %s'%file_argument)
    if os.path.isdir(file_argument):
        print('argument shoud be a media file, not a directory. Bye...')
        quit()
    # print(file_argument)
    if not os.path.exists(file_argument):
        print('%s does not exist, bye'%file_argument)
        quit()
    errors, DF_flag, fps_rel_to_audio, LTC_frames_and_pos = ltcdump_and_check(file_argument, LTC_chan)
    if errors:
        print('errors! %s'%errors)
        print('Some errors in those %i but detected FPS rel to audio is %0.3f%s'%(len(LTC_frames_and_pos),
                                fps_rel_to_audio, 'DF' if DF_flag else 'NDF'))
    else:
        print('\nAll %i frames are sequential and detected FPS rel to audio is %0.3f%s\n'%(len(LTC_frames_and_pos),
                                fps_rel_to_audio, 'DF' if DF_flag else 'NDF'))
    # print('trying to decode TTC...')
    with Progress(transient=True) as progress:
        task = progress.add_task("trying to decode TTC...")
        progress.start()
        m = device_scanner.media_at_path(Path(file_argument))
        logger.debug('media_at_path %s'%m)
        recording = yaltc.Recording(m, )
        logger.debug('Rec %s'%recording)
        time = recording.get_start_time(progress=progress, task=task)
    if time == None:
        print('Start time couldnt be determined')
    else:
        audio_samplerate_gps_corrected = recording.true_samplerate
        audio_error = audio_samplerate_gps_corrected/recording.get_samplerate()
        gps_corrected_framerate = fps_rel_to_audio*audio_error  
        print('gps_corrected_framerate',gps_corrected_framerate,audio_error)
        frac_time = int(time.microsecond / 1e2)
        d = '%s.%s'%(time.strftime("%Y-%m-%d %H:%M:%S"),frac_time)
        base = os.path.basename(file_argument)
        print('%s UTC:%s pulse: %i on chan %i'%(base, d,
                    recording.sync_position,
                    recording.TicTacCode_channel))
        print('audio samplerate (gps)', audio_samplerate_gps_corrected)
        all_channels_data = read_whole_audio_data(file_argument)
        TTC_data = all_channels_data[recording.TicTacCode_channel]
        sec_and_pulses = find_pulses(TTC_data, recording)
        secs, pulses = list(zip(*sec_and_pulses))
        pulses = list(pulses)
        logger.debug('pulses %s'%pulses)
        samples_between_UTC_pulses = []
        for n1, n2 in zip(pulses[1:], pulses):
            delta = n1 - n2
            if np.isclose(delta, audio_samplerate_gps_corrected, rtol=1e-3):
                samples_between_UTC_pulses.append(delta - audio_samplerate_gps_corrected)
        samples_between_UTC_pulses = np.array(samples_between_UTC_pulses)
        pulse_length_std = samples_between_UTC_pulses.std()
        max_min_over_2 = abs(samples_between_UTC_pulses.max() - samples_between_UTC_pulses.min())/2
        # print(samples_between_UTC_pulses)
        # print('time is measured with a precision of %f audio samples'%(pulse_length_std))
        precision = 1e6*max_min_over_2/audio_samplerate_gps_corrected
        print('Time is measured with a precision of %0.1f audio samples (%0.1f μs)'%(max_min_over_2, precision))
        frame_duration = 1/fps_rel_to_audio
        rel_min_error = 100*1e-6*precision/frame_duration
        print('so LTC syncword jitter less than %0.1f %% wont be detected'%(rel_min_error))
        # fig, ax = plt.subplots()
        # n, bins, patches = ax.hist(samples_between_UTC_pulses)
        # plt.show()
        # x = range(len(pulses))
        a, b = np.polyfit(pulses, secs, 1)
        logger.debug('slope, b = %f %f'%(a,b))
        # sr_slope = 1/a
        # print(sr_slope/recording.true_samplerate)
        coherent_sr = np.isclose(a*audio_samplerate_gps_corrected, 1, rtol=1e-7)
        logger.debug('samplerates (slope VS rec) are close: %s ratio %f'%(coherent_sr,
                                    a*audio_samplerate_gps_corrected))
        if not coherent_sr:
            print('warning, wav samplerate are incoherent (Rec + Decode VS slope)')
        def make_sample2time(a, b):
            return lambda n : a*n + b 
        sample2time = make_sample2time(a, b)
        logger.debug('sample2time fct: %s'%sample2time)
        LTC_samples = [N for _, N in LTC_frames_and_pos]
        LTC_times = [sample2time(N) for N in LTC_samples]
        slope_fps, _ = np.polyfit(LTC_times, range(len(LTC_times)), 1)
        print('slope_fps l329', ppm(slope_fps,24))
        print('diff slope, ppm',ppm(gps_corrected_framerate, slope_fps))
        LTC_frame_durations_samples = [a - b for a, b in zip(LTC_samples[1:], LTC_samples)]
        # print(LTC_frame_durations_samples)
        frame_duration = 1/fps_rel_to_audio 
        errors_useconds = [1e6*(frame_duration -(a - b)) for a, b in zip(LTC_times[1:], LTC_times)]
        # print(errors_useconds)
        errors_useconds = np.array(errors_useconds)
        LTC_std = abs(errors_useconds).std()
        LTC_max_min = abs(errors_useconds.max() - errors_useconds.min())/2
        # print('Mean frame duration is %i audio samples'%)
        print('\nhere LTC frame duration varies by %f μs ('%LTC_max_min, end='')
        print('%0.3fFPS nominal frame duration is %0.0f μs)\n'%(fps_rel_to_audio, 1e6/fps_rel_to_audio))
        # print(errors_useconds[:200])
        # audio_sampling_period = 1/samplerate
        # print(audio_sampling_period)
        # errors_in_audiosamples = [int(e/audio_sampling_period) for e in errors_seconds]
        # print(delta_milliseconds)
        # plt.plot(LTC_times, marker='.', markersize='1',
        #     linestyle='None', color='black')
        # plt.show()
        # print(LTC_times)
        # fig, ax = plt.subplots()

        # the histogram of the data
        # print(errors_in_audiosamples)
        fig, ax = plt.subplots()
        n, bins, patches = ax.hist(errors_useconds, bins=40)
        plt.show()
    quit()

if __name__ == '__main__':
    main()

#     import matplotlib.pyplot as plt
# import numpy as np

# rng = np.random.default_rng(19680801)

# # example data
# mu = 106  # mean of distribution
# sigma = 17  # standard deviation of distribution
# x = rng.normal(loc=mu, scale=sigma, size=420)

# num_bins = 42

# fig, ax = plt.subplots()

# # the histogram of the data
# n, bins, patches = ax.hist(x, num_bins, density=True)

# # add a 'best fit' line
# y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
#      np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
# ax.plot(bins, y, '--')
# ax.set_xlabel('Value')
# ax.set_ylabel('Probability density')
# ax.set_title('Histogram of normal distribution sample: '
#              fr'$\mu={mu:.0f}$, $\sigma={sigma:.0f}$')

# # Tweak spacing to prevent clipping of ylabel
# fig.tight_layout()
# plt.show()
