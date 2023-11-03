import os
import scipy.io.wavfile as wav
import sys
from deepspeech.model import Model
import subprocess
import configparser

class DSDecoder:

    def __init__(self, lstfile, no_ext, config_file, test=False):
        '''
        Takes in a list of possible words to be said and a path to which language files will be made
        '''
        #Should be from config.ini
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.model= self.config['deepspeech']['MODEL']
        self.alphabet = self.config['deepspeech']['ALPHABET']
        self.binary = self.config['deepspeech']['BINARY']
        self.trie = self.config['deepspeech']['TRIE']
        self.kenlm = self.config['kenlm']['PATH']
        self.n_feat = self.config.getint('deepspeech','N_FEATURES')
        self.n_context = self.config.getint('deepspeech','N_CONTEXT')
        self.n_beam = self.config.getint('deepspeech','BEAM_WIDTH')
        self.no_ext = no_ext
        self.lstfile = lstfile
        self.lm, self.trie = self._create_lm()
        self.decoder = Model(self.model, self.n_feat, self.n_context, self.alphabet, self.n_beam)
        self.decoder.enableDecoderWithLM(self.alphabet, self.lm, self.trie, 4, 1, 3)

    def decode(self, wavfile):
        '''
        Takes in a wavfile, returns a list of words Deepspeech thinks was said.
        '''

        fs, audio = wav.read(wavfile)
        transcription = self.decoder.stt(audio, fs).strip().split(' ')
        words_in_transcription = [x for x in transcription if x]
        return words_in_transcription

    def _create_lm(self):
        '''
        This uses utilities included from the DeepSpeech Github as well as kenlm to create language models.
        '''

        devnull = open(os.devnull, 'w')

        with open(self.lstfile,'r') as lst:
            words = [x.rstrip().strip('\n') for x in lst]
        # makes it into a bigram model, necessary for kenlm
        bigram_lst = self.no_ext + '_bigram.lst'
        with open(bigram_lst, 'w') as bigram_file:
            lower_lst = [x.lower() for x in words]
            for line in lower_lst:
                for line2 in lower_lst:
                    bigram_file.write(line.lower() + ' ' + line2.lower() + '\n')
                with open(self.lstfile + '.tmp', 'w') as lstfile_tmp:
                    lstfile_tmp.write(line.lower())

        lstfile = self.lstfile + '.tmp'

        #run kenlm
        subprocess.call("{} -o 2 -S 1G -T '{}.tmp' --discount_fallback < '{}' >'{}.arpa'"
                        .format(self.kenlm, self.no_ext, bigram_lst, self.no_ext),
                        #stdout=devnull,
                        #stderr=devnull,
                        shell=True)

        # makes binary out of arpa file
        subprocess.call("'{}' '{}.arpa' '{}.bin'".format(self.binary, self.no_ext, self.no_ext),
                        # stdout=devnull,
                        # stderr = devnull,
                        shell=True)

        # creates trie for deepspeech
        subprocess.call(
            "'{}' '{}' '{}' '{}' '{}'".format(self.trie, self.alphabet, self.no_ext + '.bin', lstfile, self.no_ext + '.trie'),
            # stdout=devnull,
            # stderr = devnull,
            shell=True)

        return self.no_ext + '.bin', self.no_ext + '.trie'

    def cleanup(self):
        # Remove .transcript
        try:
            os.remove(self.lm)
        except OSError:
            pass

        # Remove .arpa
        try:
            os.remove(self.trie)
        except OSError:
            pass



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('python3', sys.argv[0], 'file.wav', 'file.lst')
        sys.exit(0)
    wavfile = sys.argv[1]
    lstfile = sys.argv[2]
    # tmpfile = sys.argv[3]
    with open(lstfile) as lstf:
        words = [list(x.rstrip('\n')) for x in lstf]
    print(DSDecoder(lstfile, lstfile.split('.')[0], '/home1/maint/automatic_annotation/config/config.ini').decode(wavfile))
