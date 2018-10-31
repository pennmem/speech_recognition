import os
import pickle
import numpy as np
from scripts import utils
from pattern.text.en import singularize
import difflib
from collections import defaultdict

import re

subjects = [u'R1375C', u'R1361C', u'R1123C', u'R1325C', u'R1364C', u'R1114C', u'R1063C',
 u'R1122E', u'R1385E', u'R1057E', u'R1423E', u'R1433E', u'R1172E', u'R1161E',
 u'R1281E', u'R1275D', u'R1155D', u'R1104D', u'R1100D', u'R1166D', u'R1032D',
 u'R1154D', u'R1345D', u'R1401J', u'R1310J', u'R1049J', u'R1431J', u'R1191J',
 u'R1092J', u'R1081J', u'R1236J', u'R1131M', u'R1198M', u'R1031M', u'R1042M',
 u'R1324M', u'R1332M', u'R1412M', u'R1039M', u'R1232N', u'R1142N', u'R1304N',
 u'R1118N', u'R1162N', u'R1175N', u'R1149N', u'R1250N', u'R1186P', u'R1067P',
 u'R1221P', u'R1003P', u'R1006P', u'R1066P', u'R1148P', u'R1089P', u'R1358T',
 u'R1125T', u'R1070T', u'R1138T', u'R1077T', u'R1203T', u'R1113T', u'R1134T']

spanish = ['R1039M', 'R1070T', 'R1134T', 'R1250N', 'R1186P']

with open('cmudict.pkl','rb') as cmu:
    cmu_dict = pickle.load(cmu)

def remove_nonalpha(string):
    return re.sub(r'\W+', '', string)

def word2phone(word):
   return default_dict(cmu_dict, word)

def closest_word(word, words, modify_dict, min_dist= 999):
    min_distance = min_dist
    closest_word = word
    for w in words:
        seq = difflib.SequenceMatcher(None, word, w)
        blocks = seq.get_matching_blocks()
        match_num = sum([block.size for block in blocks])
        # largest_match = max([block.size for block in blocks])
        wordlen = max(len(word), len(w))


        distance = wordlen - match_num

        if distance < min_distance: ## or largest_match >2:
            min_distance = distance
            closest_word = w
            # print(distance)
            # print(word)
            # print(wordlen)
            # print(closest_word)
            # print(default_dict(modify_dict,closest_word))

    return closest_word

def default_dict(dict, key):
    if key in dict:
        return dict[key]
    else:
        return key

def parse(pklfile, words, modify_dict):
    good_words = []
    with open(pklfile,'rb') as pkl:
        x = pickle.load(pkl)
    final_transcript = []
    for result in x.results:
        alts = result.alternatives[:5]
        for _, alt in enumerate(alts):
            trans = alt.transcript
            raw_words = [x.lower() for x in trans.split(' ') if x]
            good_words.extend([x for x in raw_words if x in words])
            good_words.extend([remove_nonalpha(x) for x in raw_words if remove_nonalpha(x) in words])
            good_words.extend([singularize(x) for x in raw_words if singularize(x) in words])
            good_words.extend([singularize(remove_nonalpha(x)) for x in raw_words if singularize(remove_nonalpha(x)) in words])
            good_words.extend([modify_match(x,modify_dict,1) for x in raw_words if modify_match(x, modify_dict,1) in words])
    good_words = set(good_words)
    return good_words


def parse_read(pklfile):
    good_words = []
    with open(pklfile,'rb') as pkl:
        x = pickle.load(pkl)
    return x


def modify(x):
    return word2phone(singularize(remove_nonalpha(x.lower())))
#return word2phone(singularize)

def modify_match(x, modify_dict, num=1):
    return default_dict(modify_dict,
                        closest_word(modify(x),
                                     [x for x in modify_dict],
                                     modify_dict,
                                     num))
    # return x

def alt_main():
    gs_total = []
    fns_dict = defaultdict(int)
    fps_dict = defaultdict(int)
    subject_dict = {}
    for subject in subjects:
        if subject not in spanish:
            print(subject)
            tp = []
            fp = []
            fn = []
            tl = []
            for num in range(24):
                annfile = '/data/eeg/{}/behavioral/FR1/session_0/{}.ann'.format(subject, num)
                lstfile = '/data/eeg/{}/behavioral/FR1/session_0/{}.lst'.format(subject, num)
                pklfile = '/scratch/francob/big_ram_analyses_alternatives/{}/{}.pkl'.format(subject, num)
                gs_seen = []
                ds_seen = []
                real_hits = []
                if os.path.exists(lstfile):
                    raw_words = [x.rstrip('\n').strip().lower() for x in open(lstfile)]
                    modify_dict = {modify(x):x for x in raw_words}

                    if (os.path.exists(pklfile)):
                        gs_seen = [x.lower() for x in parse(pklfile, raw_words, modify_dict) if x.lower() in raw_words]


                    if (os.path.exists(annfile)):
                        with open(annfile, 'rb') as ann:
                            real_hits = [x['word'].lower() for x in utils.read_ann(annfile) if x['word'].lower() in raw_words]


                    if gs_seen:
                        # print('Real words')
                        # print(real_hits)
                        # print('Cloud')
                        # print(gs_seen)

                        temp_tp = len(set(gs_seen).intersection(set(real_hits)))
                        temp_fp = len(set(gs_seen) - set(real_hits))
                        temp_fn = len(set(real_hits) - set(gs_seen))
                        temp_tl = len(set(real_hits))


                        tp.append(temp_tp)
                        fp.append(temp_fp)
                        fn.append(temp_fn)
                        tl.append(temp_tl)

                        temp_fns = [x for x in set(real_hits) - set(gs_seen)]
                        for x in temp_fns:
                            fns_dict[x] += 1

                        temp_fps = [x for x in set(gs_seen) - set(real_hits)]
                        for x in temp_fps:
                            fps_dict[x] += 1

                        if temp_fn + temp_fp > 0:
                            print(subject, num)
                            print('real_hits')
                            print(list(real_hits))
                            print('gs_seen')
                            print(list(gs_seen))
                            # print('raw_phonemes')
                            # print(list(raw_phonemes))

            total_diff = ((sum(tl) - sum(fp) - sum(fn)) / float(max(sum(tl), 1)))
            if sum(tl):
                gs_total.append([total_diff, sum(tp), sum(fp), sum(fn), sum(tl)])
                subject_dict[subject] = total_diff

    diffs = [x[0] for x in gs_total]
    tps = [x[1] for x in gs_total]
    fps = [x[2] for x in gs_total]
    fns = [x[3] for x in gs_total]
    tls = [x[4] for x in gs_total]
    print(fns_dict)
    print(fps_dict)

    print([(x, subject_dict[x]) for x in sorted(subject_dict, key=subject_dict.get, reverse=True)])
    print(diffs)
    # print(tls)
    print((sum(tls) - sum(fps) - sum(fns)) / float(sum(tls)))
    print(sum(fps) / float(sum(tls)))
    print(sum(fps))
    print(sum(fns))
    print(sum(fns) / float(sum(tls)))
    print(np.mean([subject_dict[x] for x in subject_dict]))
    # print(subject_dict)
    location_dict = {}
    for subject in subject_dict:
        if subject[-1] in location_dict:
            location_dict[subject[-1]].append(subject_dict[subject])
        else:
            location_dict[subject[-1]] = [subject_dict[subject]]
    print(location_dict)
    for location in location_dict:
        print(location)
        print(np.mean(location_dict[location]))


def main():
    gs_total = []
    fns_dict = defaultdict(int)
    fps_dict = defaultdict(int)
    subject_dict = {}
    for subject in subjects:
        if subject not in spanish:
            print(subject)
            tp = []
            fp = []
            fn = []
            tl = []
            for num in range(24):
                annfile = '/data/eeg/{}/behavioral/FR1/session_0/{}.ann'.format(subject, num)
                lstfile = '/data/eeg/{}/behavioral/FR1/session_0/{}.lst'.format(subject, num)
                pklfile = '/scratch/francob/big_ram_analyses/{}/{}.pkl'.format(subject, num)
                gs_seen = []
                ds_seen = []
                real_hits = []
                if os.path.exists(lstfile):
                    raw_words = [x.rstrip('\n').strip().lower() for x in open(lstfile)]
                    raw_phonemes = [modify(x) for x in raw_words]
                    modify_dict = {modify(x):x for x in raw_words}

                    if (os.path.exists(pklfile)):
                        gs_raw = [x.lower() for x in parse(pklfile)]
                        modified = [modify_match(x, modify_dict) for x in gs_raw]
                        gs_seen = set(x for x in modified if x in raw_words)

                    if (os.path.exists(annfile)):
                        with open(annfile, 'rb') as ann:
                            raw_ann =[x['word'] for x in utils.read_ann(annfile)]
                            real_hits = set(modify_match(x, modify_dict) for x in raw_ann if modify_match(x, modify_dict) in raw_words)
                            # real_hits = set(x for x in raw_ann if x in raw_words)

                    if gs_seen:
                        # print('Real words')
                        # print(real_hits)
                        # print('Cloud')
                        # print(gs_seen)

                        temp_tp = len(set(gs_seen).intersection(set(real_hits)))
                        temp_fp = len(set(gs_seen) - set(real_hits))
                        temp_fn = len(set(real_hits) - set(gs_seen))
                        temp_tl = len(set(real_hits))
                        tp.append(temp_tp)
                        fp.append(temp_fp)
                        fn.append(temp_fn)
                        tl.append(temp_tl)

                        temp_fns = [x for x in set(real_hits) - set(gs_seen)]
                        for x in temp_fns:
                            fns_dict[x]+=1

                        temp_fps = [x for x in set(gs_seen) - set(real_hits)]
                        for x in temp_fps:
                            fps_dict[x]+=1


                        if temp_tl != temp_tp:
                            print(subject, num)
                            print('real_hits')
                            print(list(real_hits))
                            print('gs_seen')
                            print(list(gs_seen))
                            print('modified')
                            print(list(modified))
                            # print('raw_phonemes')
                            # print(list(raw_phonemes))
                            print('raw_ann')
                            print(raw_ann)
                            print('gs_raw')
                            print(list(gs_raw))

            total_diff = ((sum(tl) - sum(fp) - sum(fn))/float(max(sum(tl),1)))
            if sum(tl):
                gs_total.append([total_diff,  sum(tp), sum(fp), sum(fn), sum(tl)])
                subject_dict[subject] = total_diff

    diffs = [x[0] for x in gs_total]
    tps = [x[1] for x in gs_total]
    fps = [x[2] for x in gs_total]
    fns = [x[3] for x in gs_total]
    tls = [x[4] for x in gs_total]
    print(fns_dict)
    print(fps_dict)

    print([(x, subject_dict[x]) for x in sorted(subject_dict, key = subject_dict.get, reverse=True)])
    print(diffs)
    # print(tls)
    print((sum(tls) - sum(fps) - sum(fns))/float(sum(tls)))
    print(sum(fps)/float(sum(tls)))
    print(sum(fns)/float(sum(tls)))
    print(np.mean([subject_dict[x] for x in subject_dict]))
    # print(subject_dict)
    location_dict = {}
    for subject in subject_dict:
        if subject[-1] in location_dict:
            location_dict[subject[-1]].append(subject_dict[subject])
        else:
            location_dict[subject[-1]] =[subject_dict[subject]]
    print(location_dict)
    for location in location_dict:
        print(location)
        print(np.mean(location_dict[location]))




if __name__ =='__main__':
    # parse_google_cloud()
    # parse_deepspeech()

    alt_main()