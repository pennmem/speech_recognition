import collections
import subprocess
import contextlib
import sys
import wave
import webrtcvad
import glob
import os

def read_wave(path):
    """Reads a .wav file.

    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.

    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.

    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.

    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.

    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.

    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.

    Arguments:

    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        #sys.stdout.write(
        #    '1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                #sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                start_time = ring_buffer[0].timestamp
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                #sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield (b''.join([f.bytes for f in voiced_frames]), start_time)
                ring_buffer.clear()
                voiced_frames = []
    #if triggered:
        #sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    #sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield (b''.join([f.bytes for f in voiced_frames]), frame.timestamp)


def return_silence(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.

    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.

    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.

    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.

    Arguments:

    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False
    silent = []
    voiced_frames = []
    for frame in frames:
        #sys.stdout.write(
        #    '1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                start_time = ring_buffer[0].timestamp
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()

        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                triggered = False
                ring_buffer.clear()
                voiced_frames = []
        if triggered:
            silent.append(0)
        else:
            silent.append(1)
    return silent

class WavChunk():
    def __init__(self, wavfile, start_time, end_time):
        self.wavfile = wavfile
        self.start_time = start_time
        self.end_time = end_time


def split_on_silence(wavfile, dest_directory):
    '''
    :param wavfile:
    :param dest_directory:
    :return:
    '''
    if type(wavfile) is list:
        wavfile = wavfile[0]

    audio, sample_rate = read_wave(wavfile)
    vad = webrtcvad.Vad(1)
    frames = frame_generator(10, audio, sample_rate)
    frames = list(frames)
    segments = return_silence(sample_rate, 10, 100, vad, frames)
    long_silences = []
    consecutive_ones = 0
    start = 0

    #If there are periods of silence longer than a second, append 300ms from the start of silence to 300ms to the end of silence.
    for i, segment in enumerate(segments):
        if segments[i] == 1:
            if consecutive_ones == 0:
                start = i
            consecutive_ones += 1
            if i==len(segments)-1:
                if consecutive_ones>100:
                    long_silences.append((start+30,i-30))
        else:
            if consecutive_ones>100:
                long_silences.append((start+30,i-30))
            consecutive_ones = 0
    print(long_silences)

    start_times=[]
    end_times=[]
    end = 0
    start_times.append(end)
    frames = [f.bytes for f in frames]
    voiced_frames=[]

    for i,ls in enumerate(long_silences):
        print(i)
        voiced_frames.append(frames[end:ls[0]])
        end = ls[1]
        start_times.append(end)
        end_times.append(ls[0])
    voiced_frames.append(frames[end:len(frames)-1])
    if frames[end:len(frames)-1]:
        end_times.append(len(frames)-1)
    count = 0

    paths = []
    base = os.path.basename(wavfile)
    no_ext = os.path.splitext(base)[0]
    for chunk in voiced_frames:
        byte_chunk = b''.join(chunk)
        path = os.path.join(dest_directory,  no_ext + '_{}.wav'.format(count))
        paths.append(path)
        write_wave(path, byte_chunk, sample_rate)
        count +=1

    start_times = [x*10 for x in start_times]
    end_times = [x*10 for x in end_times]
    with open(wavfile.split('.')[0] + '.times','w') as time_log:
        for pair in zip(start_times, end_times):
            time_log.write(str(pair[0]) + ' ' + str(pair[1]) + '\n')
    ziplist = list(zip(paths, start_times, end_times))
    wavchunklist = [WavChunk(x[0],x[1],x[2]) for x in ziplist]
    return wavchunklist
