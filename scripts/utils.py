import subprocess
import os

class Annotation:
    def __init__(self, word, time):
        self.word = word
        self.time = time

class AnnotationWithOffsets:
    def __init__(self, word, onset, offset):
        self.word = word
        self.onset = onset
        self.offset = offset

def times_from_ann(ann_file):
    '''
    Takes in an annotation file and returns times.
    :param ann_file: Path to annotation file
    :return: List of words
    '''
    ann_list =[line.rstrip('\n') for line in open(ann_file)]
    ann_list =[line for line in ann_list if line]
    ann_list =[line for line in ann_list if line[0]!='#' and line[0]!='<']

    #This handles some very specific anns.
    for i, j in enumerate(ann_list):
        if j[0] =='=':
            ann_list = ann_list[:i]
    time_list =[float(line.split('\t')[-3].lower()) for line in ann_list]
    return time_list


def words_from_ann(ann_file):
    '''
    Takes in an annotation file and returns the words.
    :param ann_file: Path to annotation file
    :return: List of words
    '''
    ann_list =[line.rstrip('\n') for line in open(ann_file)]
    ann_list =[line for line in ann_list if line]
    ann_list =[line for line in ann_list if line[0]!='#' and line[0]!='<']

    #This handles some very specific anns.
    for i, j in enumerate(ann_list):
        if j[0] =='=':
            ann_list = ann_list[:i]

    word_list =[line.split('\t')[-1].lower() for line in ann_list]
    return word_list

def read_ann(ann_file):
    '''
    Takes in an annotation file and returns a list of dicts with keys "word" and "time".
    :param ann_file: Path to annotation file
    :return: List of dicts
    '''
    zip_list = zip(words_from_ann(ann_file), times_from_ann(ann_file))
    ann_list = [{"word": x[0], "time":x[1]} for x in zip_list]
    return ann_list

def add_ann(annotations, offset):
    '''
    Takes in a list of annotations and returns the list with each time added to by offset
    :param annotation:
    :param offset:
    :return:
    '''
    return [Annotation(x.word, x.time+offset) for x in annotations]

def downsample(src, dest, rate):
    '''
    Takes in file from src and downsamples
    :param src:
    :param dest:
    :param rate:
    :return:
    '''
    # Wraps ffmpeg, it was quicker than whenever I tried anything native. You have to copy to get it to go to the same
    # file, otherwise a (silent) error happens.
    if src == dest:
        tmp_file = '{}_tmp.wav'.format(os.path.splitext(src)[0])
        subprocess.call('/home1/maint/ffmpeg-3.4.2-64bit-static/ffmpeg -y -i {} -ar {} {}'.format(src, rate, tmp_file), shell=True, stderr=subprocess.STDOUT)
        subprocess.call('mv {} {}'.format(tmp_file, dest), shell=True, stderr=subprocess.STDOUT)
    else:
        subprocess.call('/home1/maint/ffmpeg-3.4.2-64bit-static/ffmpeg -y -i {} -ar {} {}'.format(src, rate, dest),shell=True, stderr=subprocess.STDOUT)
    return

def words_from_lst(lstfile):
    return [x.rstrip('\n') for x in open(lstfile)]

def get_subject(filename):
    return filename.split('/')[6]

def get_session(filename):
    return filename.split('/')[7].split('_')[-1]

