import os
import sys
from kaldi_align import KaldiDecoder
import configparser

def annotate(wavfile, lstfile, config_file, exp_config_file):

    exp_config = configparser.ConfigParser(allow_no_value=True)
    exp_config.read(exp_config_file)
    root = []
    log = []


    try:
        exp_config = dict(exp_config.items('properties'))
        root = exp_config['experiment_root']
        log = exp_config['log']
        finished_sessions = exp_config['finished_sessions']
    except Exception:
        raise

    no_ext = os.path.splitext(wavfile)[0]
    kd = KaldiDecoder(lstfile, no_ext, config_file)
    kaldi_ann = kd.decode(wavfile)

    with open(log,'a') as l:
        l.write(wavfile + '\n')
        l.write(' '.join([x.word for x in kaldi_ann])+'\n')

    if kaldi_ann:
        if all([x.word != '<unk>' for x in kaldi_ann]):
            kd.write_ann(kaldi_ann, no_ext)
    # kd.cleanup()


if __name__ == "__main__":
    wavfile = sys.argv[1]
    lstfile = sys.argv[2]
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('/home1/maint/speech_recognition_scripts/config.ini')
    annotate(wavfile,lstfile,config)


