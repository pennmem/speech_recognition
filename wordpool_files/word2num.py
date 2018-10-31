import read_ann
import pickle
import os
import glob
import sys

word2numdict = pickle.load(open('/home1/francob/new_speech_recognition_scripts/word2numdict.pickle', 'rb'))

def fix_ann(ann_file):
    annotation = read_ann.read_all(ann_file)
    with open(ann_file,'w') as ann:
        for x in annotation:
            word = x[0]
            time = x[1]
            if word in word2numdict:
                temp_num = word2numdict[word.lower()]
            else:
                temp_num = -1
            ann.write('{}\t{}\t{}\n'.format(time,temp_num,word.upper()))

def main():
    for ann in glob.glob('/home1/francob/franco_annotate_files/*/*.ann'):
        fix_ann(ann)

if __name__ == '__main__':
    main()

