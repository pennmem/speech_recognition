import os
import sys
from kaldi_align import KaldiDecoder
import configparser

def annotate(wavfile, lstfile, config_file, exp_config_file):

    with open(lstfile) as lstf:
        words = [x.rstrip('\n').rstrip() for x in lstf]

    no_ext = os.path.splitext(wavfile)[0]
    kd = KaldiDecoder(words, no_ext, config_file, exp_config_file)
    kaldi_ann = kd.decode(wavfile)
    with open('/data/eeg/scalp/ltp/VFFR/error_asr_log.txt','a') as l:
        l.write(wavfile + '\n')
        l.write(' '.join([x.word for x in kaldi_ann])+'\n')

    if kaldi_ann:
        if all([x.word != '<unk>' for x in kaldi_ann]):
            kd.write_ann(kaldi_ann, no_ext)
    kd.cleanup()


if __name__ == "__main__":
    wavfile = sys.argv[1]
    lstfile = sys.argv[2]
    config = configparser.ConfigParser()
    config.read('/home1/maint/speech_recognition_scripts/config.ini')
    annotate(wavfile,lstfile,config)


