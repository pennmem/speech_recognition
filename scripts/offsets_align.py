import os
import numpy as np
from kaldi_align import KaldiDecoder
import utils
#generate transcripts

def find_offset_match(annotations, offset_annotations):
    offsets = [[] for _ in annotations] #This stores the offsets for each word in annotation

    for i, ann in enumerate(annotations):
        matching_words = [oann for oann in offset_annotations if oann.word.upper() == ann.word.upper()]
        if matching_words:
            min_time = min(matching_words, key = lambda x: np.abs(ann.time-x.onset))
            offsets[i] = utils.AnnotationWithOffsets(ann.word, ann.time, min_time.offset)
        else:
            if i < len(annotations) - 2:
                closest_unk = [oann.offset for oann in offset_annotations if oann.offset < annotations[i+1].time - 100]
                if closest_unk:
                    offsets[i] = utils.AnnotationWithOffsets(ann.word, ann.time, closest_unk[-1])
                else:
                    offsets[i] = utils.AnnotationWithOffsets(ann.word, ann.time, ann[i+1].time - 1)
            else:
                closest_unk = [oann.offset for oann in offset_annotations]
                if closest_unk:
                    offsets[i] = utils.AnnotationWithOffsets(ann.word, ann.time, closest_unk[-1])
                else:
                    offsets[i] = utils.AnnotationWithOffsest(ann.word, ann.time, ann.time+1000)
    return offsets

def create_offsets(wavfile, lstfile, annfile, config_file):

    no_ext = os.path.abspath(wavfile).split('.')[0]
    words = [x.strip().rstrip('\n') for x in open(lstfile)]
    transcription_file = create_transcript(no_ext, words)
    kd = KaldiDecoder(transcription_file, no_ext, config_file)
    kaldi_oann = kd.decode(wavfile, offsets=True)
    kd.cleanup()
    offsets = find_offset_match(utils.read_ann(annfile), kaldi_oann)
    kd.write_oann(offsets, no_ext)
    return offsets

def create_transcript(no_ext, transcription):
    '''
    Creates a .transcript file that contains all the words in words, separated by a newline. This needs to happen
    because the shell scripts need to run on files so we can't pass in word list.
    '''

    transcription_file = no_ext + '.transcript'
    with open(transcription_file, 'w') as tf:

        # the newline is needed for language model creation to work.
        tf.write(' '.join(transcription).upper() +'\n')
    return transcription_file

