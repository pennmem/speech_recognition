import os
import subprocess
import utils
import glob
import pickle


class Times:
    def __init__(self, start, end, num):
        self.start = start
        self.end = end
        self.num = num

def check_all_exist(directory):
    '''
    Takes a directory and returns True if each ann file has a matching wavfile, False otherwise
    '''
    wavfiles = glob.glob(directory+'*.wav')
    annfiles = glob.glob(directory+'*.ann')
    wavfile_noext = set([os.splitext(f)[0] for f in wavfiles])
    annfiles_noext = set([os.splitext(f)[0] for f in wavfiles])
    if wavfile_noext == annfiles_noext:
        return True
    return False

def check_is_empty(annfile):
    '''
    Takes an annotation file and returns True is 'NA' is in the annotation
    '''
    annotation = utils.read_ann(annfile)
    if "NA" in annotation:
        return True
    return False

def write_ann(annotation, dest, word2numdict_path):
    word2numdict = pickle.load(open(word2numdict_path, 'rb'))
    with open(dest+'.ann', 'w') as af:
        for pair in annotation:
            word = pair.word
            word = word.upper()
            time = pair.time
            word_key = word.lower()
            if word_key in word2numdict:
                word_num = word2numdict[word.lower()]
            else:
                word_num = -1
            af.write('{}\t{}\t{}\n'.format(time, word_num, word))


def write_par_file(annlist, dest):
    with open(dest,'w') as parf:
        for x in annlist:
            parf.write('{}\t{}\n'.format(x.word, x.time))

def read_time_file(time_file):
    raw_times = [line.rstrip('\n').split(' ') for line in open(time_file)]
    times = [Times(x[0], x[1], i) for i, x in enumerate(raw_times)]
    return times

def get_onset(Annotation):
    return Annotation.time

def check_within_times(time_to_check, times):
    for time in times:
        if (float(time_to_check)>= float(time.start) and float(time_to_check) < float(time.end)):
            return True
    return False


def combine_chunks(wavfile, target_directory):
    '''
    Finds the chunks of a wavfile, then combines them and outputs a sorted Annotation
    :param wavfile:
    :param current_directory:
    :param target_directory:
    :return:
    '''
    no_ext = wavfile.split('.')[0]
    ann_file = no_ext+'.ann'
    base_name = os.path.basename(no_ext)
    time_file = no_ext +'.times'
    ann = []
    if os.path.exists(time_file):
        times = read_time_file(time_file)
        if os.path.exists(ann_file):
            ann = [x for x in utils.read_ann(ann_file) if not check_within_times(x.time, times)]
        for i, time in enumerate(times):
            chunk_ann = []
            chunk_ann_file = os.path.join(target_directory, base_name+'_'+str(i)+'.ann')
            if os.path.exists(chunk_ann_file): #MD changed from ann_file 4/28/21
                chunk_ann = utils.read_ann(chunk_ann_file)
            ann.extend([utils.Annotation(x.word, x.time+float(time.start))
                        for x in chunk_ann if x.word.upper()!='NA'])
        print([x.time for x in ann])
        ann = sorted(ann, key = get_onset)
    else:
        ann = []
    return ann

def combine_main_directory_annotated_files(wavfile, word2numdict):
    '''
    Finds the chunks of a wavfile in the main directory, combines them, then writes .ann files
    :param wavfile:
    :param word2numdict:
    :return:
    '''
    wavfile = os.path.abspath(wavfile)
    base_name = os.path.splitext(os.path.basename(wavfile))[0]
    dir_path = os.path.dirname(wavfile)
    chunk_dir = os.path.join(dir_path, 'chunks/')
    fta_dir = os.path.join(dir_path, 'files_to_annotate/')
    time_file = os.path.splitext(wavfile)[0]+'.times'
    if os.path.exists(time_file):
        times = read_time_file(time_file)
    chunks = [os.path.join(chunk_dir, base_name+'_'+str(x)+'.wav') for x in range(len(times))]
    for chunk in chunks:
        chunk_anns = combine_chunks(chunk, fta_dir)
        write_ann(chunk_anns, os.path.splitext(os.path.abspath(chunk))[0], word2numdict)
    combined_anns = combine_chunks(wavfile, chunk_dir)
    write_ann(combined_anns, os.path.splitext(os.path.abspath(wavfile))[0], word2numdict)
