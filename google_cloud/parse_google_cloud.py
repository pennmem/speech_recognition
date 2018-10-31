import pickle
import os
from scripts import utils

subjects = ['R1001P',
'R1010J',
'R1084T',
'R1085C',
'R1162N',
'R1004D',
'R1069M',
'R1075J',
'R1089P',
'R1181E']

def parse(pklfile):
    with open(pklfile,'rb') as pkl:
        x = pickle.load(pkl)
    final_transcript = []
    for result in x.results:
        wordstring = result.alternatives[0].transcript
        wordlist = [x.upper() for x in wordstring.split(' ') if x]
        final_transcript.extend(wordlist)
    return final_transcript

def parse_google_cloud():
    for subject in subjects:
        print(subject)
        for x in range(24):
            pklfile = '/Users/francob/{}/{}.pkl'.format(subject, x)
            lstfile = '/Users/francob/{}/{}.lst'.format(subject, x)
            if (os.path.exists(pklfile) and os.path.exists(lstfile)):
                words = [x.rstrip('\n').strip().upper() for x in open(lstfile)]
                response = [x for x in parse(pklfile) if x.upper() in words]

def parse_deepspeech():
    for subject in subjects:
        print(subject)
        for x in range(24):
            pklfile = '/Users/francob/ram_analyses/{}/{}.pkl'.format(subject, x)
            lstfile = '/Users/francob/ram_analyses/{}/{}.lst'.format(subject, x)

            if (os.path.exists(pklfile) and os.path.exists(lstfile)):
                words = [x.rstrip('\n').strip().upper() for x in open(lstfile)]
                with open(pklfile, 'rb') as pkl:
                    response = [x for x in pickle.load(pkl) if x.upper() in words]
                print(response)

def parse_ann():
    for subject in subjects:
        print(subject)
        for x in range(24):
            annfile = '/Users/francob/real_ann/{}/{}.ann'.format(subject, x)
            lstfile = '/Users/francob/real_ann/{}/{}.lst'.format(subject, x)
            if (os.path.exists(annfile) and os.path.exists(lstfile)):
                words = [x.rstrip('\n').strip().upper() for x in open(lstfile)]
                with open(annfile, 'rb') as ann:
                    real_hits = [x['word'].upper() for x in utils.read_ann(annfile) if x['word'].upper() in words]
                print(response)

def parse_all():
    gs_total = []
    ds_total = []
    for subject in subjects:
        print(subject)
        tp = []
        fp = []
        fn = []
        tl = []
        tp2 = []
        fp2 = []
        fn2 = []
        tl2 = []
        for x in range(24):
            annfile = '/Users/francob/real_ann/{}/{}.ann'.format(subject, x)
            lstfile = '/Users/francob/real_ann/{}/{}.lst'.format(subject, x)
            gspkl = '/Users/francob/{}/{}.pkl'.format(subject, x)
            gslst = '/Users/francob/{}/{}.lst'.format(subject, x)
            gs_seen = []
            ds_seen = []
            real_hits = []
            pklfile = '/Users/francob/ram_analyses/ram_analyses/{}/{}.pkl'.format(subject, x)



            if os.path.exists(lstfile):
                words = [x.rstrip('\n').strip().upper() for x in open(lstfile)]
                if (os.path.exists(gspkl) and os.path.exists(gslst)):
                    gs_seen = [x.upper() for x in parse(gspkl) if x.upper() in words]
                    # print('Google Cloud')
                    # print(gs_seen)

                if (os.path.exists(pklfile)):
                    words = [x.rstrip('\n').strip().upper() for x in open(lstfile)]
                    with open(pklfile, 'rb') as pkl:
                        ds_seen = [x.upper() for x in pickle.load(pkl) if x.upper() in words]

                if (os.path.exists(annfile) and os.path.exists(lstfile)):
                    with open(annfile, 'rb') as ann:
                        real_hits = [x['word'].upper() for x in utils.read_ann(annfile) if x['word'].upper() in words]

                    if gs_seen:
                        # print('Real words')
                        # print(real_hits)
                        tp.append(len(set(gs_seen).intersection(set(real_hits))))
                        fp.append(len(set(gs_seen)-set(real_hits)))
                        fn.append(len(set(real_hits)-set(gs_seen)))
                        tl.append(len(set(real_hits)))
                        if set(real_hits) != set(gs_seen):
                            print(subject, x)
                            print(real_hits)
                            print(gs_seen)

                    if ds_seen:

                        tp2.append(len(set(ds_seen).intersection(set(real_hits))))
                        fp2.append(len(set(ds_seen)-set(real_hits)))
                        fn2.append(len(set(real_hits)-set(ds_seen)))
                        tl2.append(len(set(real_hits)))

                    # if nd gs_seen:
                    #     print('Real words')
                    #     print(real_hits)
                    #     print('Deepspeech')
                    #     print(ds_seen)
                    #     print('Google Cloud')
                    #     print(gs_seen)

        gs_total.append([(sum(tl) - sum(fp) - sum(fn))/max(sum(tl),1), sum(tp), sum(fp), sum(fn), sum(tl)])
        ds_total.append([(sum(tl2) - sum(fp2) - sum(fn2))/max(sum(tl2),1), sum(tp2), sum(fp2), sum(fn2), sum(tl2)])
    print([x[0] for x in gs_total])
    print([x[0] for x in ds_total])

    data = [x[0] for x in gs_total if x[0] > 0]

if __name__ =='__main__':
    # parse_google_cloud()
    # parse_deepspeech()
    parse_all()
