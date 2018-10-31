import os
import subprocess

def unk_in(annotation):
    words = [x.word for x in annotation]
    return '<unk>' in words

class UnkRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

def get_unk_ranges(annotation, start_time, end_time):
    '''
    Finds all occurences of <unk> in an annotation. Then, it returns a range of time containing the nearest word
    before and after, or 500ms on both sides of the <unk>, whichever is bigger. In edge cases (i.e. if <unk> is the first
    word it goes to the start (end) of the wavfile.

    :param annotation:
    :param start_time:
    :param end_time:
    :return: A list of UnkRanges
    '''
    print(annotation)
    length = end_time - start_time
    final_unk_ranges = []
    unk_ranges = []


    #Finds all occurences of <unk> in an annotation. Then, it returns a range of time containing the nearest word
    #before and after, or 500ms on both sides of the <unk>, whichever is bigger. In edge cases (i.e. if <unk> is the first
    #word it goes to the start (end) of the wavfile.
    for i, x in enumerate(annotation):
        if x.word == '<unk>':
            if i < len(annotation) - 1:
                if x.time + 500 > annotation[i + 1].time:
                    if i < len(annotation) - 2:
                        end = annotation[i + 2].time
                    else:
                        end = length
                else:
                    end = annotation[i + 1].time
            else:
                end = length
            if i > 0:
                if i > 1:
                    if x.time - 500 < annotation[i - 1].time:
                        start = annotation[i - 2].time
                    else:
                        start = min(annotation[i - 1].time, max(0, x.time - 500))
                else:
                    if x.time - 500 < annotation[i - 1].time:
                        start = 0
                    else:
                        start = min(annotation[i - 1].time, max(0, x.time - 500))
            else:
                start = 0
            unk_ranges.append(UnkRange(start/float(1000), end/float(1000)))

    current_range = []

    # This combines unk_ranges if they happen to overlap. Otherwise, it provides a list of disjoint unk_ranges.
    for unk_range in unk_ranges:
        if current_range:
            if unk_range.start < current_range.end:
                current_range = UnkRange(current_range.start, unk_range.end)
            else:
                final_unk_ranges.append(current_range)
                current_range = unk_range
        else:
            current_range = unk_range

    if current_range:
        final_unk_ranges.append(current_range)

    return final_unk_ranges

def slice_wavfile(wavfile, destination, start, end):

    '''
    Creates a wavfile at destination which is a slice of wavfile from start to end, returns destination
    :param wavfile:
    :param destination:
    :param start:
    :param end:
    :return:
    '''
    devnull = open(os.devnull, 'w')
    print('ffmpeg -y -ss 00:00:{} -t 00:00:{} -i {} {}'.format(str(start), str(end), wavfile, destination))
    subprocess.call('ffmpeg -y -ss 00:00:{} -t 00:00:{} -i {} {}'.format(str(start), str(end), wavfile, destination),
                    stdout=devnull,
                    stderr=devnull,
                    shell=True)
    return destination

def add_str_before_period(string, add_string):
    split_string = string.split('.')
    return (split_string[0] + add_string + '.' + split_string[1])

def batch_slice(wavfile, destination_directory, unk_ranges):
    '''
    Creates files to annotate in destination_directory. They are of the form {session}_{chunknum}_{file_to_annotate_num}.wav
    :param wavfile:
    :param destination_directory:
    :param times:
    :return: List of created files
    '''
    print(wavfile)
    base = os.path.basename(wavfile)
    new_wavfiles = []
    for i, unk_range in enumerate(unk_ranges):
        start = unk_range.start
        end = unk_range.end
        new_base = add_str_before_period(base, '_{}'.format(i))
        final_path = os.path.join(destination_directory, new_base)
        new_wavfiles.append(
            slice_wavfile(wavfile, final_path, start, end))
    return new_wavfiles

def write_times(unk_ranges, base):
    time_file = base+'.times'
    with open(time_file,'w') as tf:
        for unk_range in unk_ranges:
            tf.write('{} {} \n'.format(unk_range.start, unk_range.end))


def make_files_to_annotate(annotation, wavfile, files_to_annotate_directory, start_time, end_time):

    '''
    :param annotation:
    :param wavfile:
    :param files_to_annotate_directory:
    :param start_time:
    :param end_time:
    :return:
    '''
    unk_ranges = get_unk_ranges(annotation, start_time, end_time)
    batch_slice(wavfile, files_to_annotate_directory, unk_ranges)
    write_times(unk_ranges, os.path.basename(wavfile))
