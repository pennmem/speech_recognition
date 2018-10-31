import os
import read_ann
import pickle
import numpy as np
import kaldi_align
#generate transcripts

#compare
def find_offset_match(annotation, automatic_offsets):
    match = [[] for _ in annotation]
    for i, word_time in enumerate(annotation):
        matching_words = [x for x in automatic_offsets if x[0].upper() == word_time[0].upper()]
        if matching_words:
            min_time = min(matching_words, key = lambda x: np.abs(word_time[1]-x[1]))
            match[i] = min_time
        else:
            if i < len(annotation) -2:
                closest_unk = [x for x in automatic_offsets if x[1] < annotation[i+1][1] - 100]
                print(closest_unk)
                if closest_unk:
                    match[i] = closest_unk[-1]
            else:
                closest_unk = [x for x in automatic_offsets]
                if closest_unk:
                    match[i] = closest_unk[-1]
    return match

def generate_offset(wavfile, lstfile, config_file):
    return


def main(wavfile, ann_file, off_file):
    words = read_ann.read_words(ann_file)
    print(words)
    no_ext = os.path.splitext(wavfile)[0]
    transcript = no_ext+'.transcript'
    print(transcript)
    with open(transcript, 'w') as tfile:
        tfile.write(' '.join(words) + '\n')
    annotation = read_ann.read_all(ann_file)
    offset_annotation = read_ann.read_all(off_file)
    print(annotation)
    # generate offsets
    automatic_offsets = kaldi_align.kaldi_align(wavfile, words, offsets=True)
    match = find_offset_match(annotation, automatic_offsets)
    return compare_match(offset_annotation, match)



if __name__ == "__main__":
    ()
    # wavfile = sys.argv[1]
    # lstfile = sys.argv[2]
    # annfile = sys.argv[3]
    #
    # no_ext = os.path.splitext(wavfile)[0]
    #
    # print(main(wavfile, lstfile, annfile))
    # word = word_time[0]
    # time = word_time[1]
    # word2numdict = pickle.load(open('/home1/maint/new_speech_recognition_scripts/word2numdict.pickle', 'rb'))
    # word_num = word2numdict[word.lower()]
    # ann_file = no_ext+'.ann'
    # with open(ann_file, 'w') as af:
    #     af.write('{}\t{}\t{}'.format(time, word_num, word))

