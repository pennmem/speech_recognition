import os
import sys
import subprocess
import pickle
import utils
import shutil
import configparser
from utils import Annotation, AnnotationWithOffsets

class KaldiDecoder:
    def __init__(self, transcript_file, no_ext, config_file):
        self.no_ext = no_ext
        self.base = os.path.basename(no_ext)
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.config_file = config_file
        self.exp_config = configparser.ConfigParser()
        self.kenlm = self.config['kenlm']['PATH']
        self.ksl = self.config['kaldi']['KALDI_SCRIPT_LOCATION']
        self.klm = self.config['kaldi']['KALDI_LM_LOCATION']
        self.dic = self.config['kaldi']['DICFILE']
        self.loc = self.config['kaldi']['KALDI_LOCATION']
        self.word2numdict_path = self.config['directories']['word_to_num_dict']

        #needs to be in this order
        self.transcript_file = transcript_file
        self.arpa = self._kenlm()
        self.tmp_directory = self._setup_lm()



    def _setup_lm(self):
        '''
        Creates language model for Kaldi and corresponding HCLG graph, see Kaldi documentation for more details.
        '''
        devnull = open(os.devnull, 'w')
        subprocess.call('{0} {1} {2} {3}'.format(self.klm, self.base, self.dic, self.arpa),
                        stdout=devnull,
                        stderr=devnull,
                        shell=True)
        return os.path.join(self.loc,self.base)

    def _kenlm(self):
        '''
        Creates an arpa file based off of the transcript, uses kenlm.
        '''
        devnull = open(os.devnull, 'w')
        subprocess.call('{} -o 2 -S 1G -T {}.tmp --discount_fallback < {} > {}.arpa'
                        .format(self.kenlm, self.no_ext, self.transcript_file, self.no_ext),
                        stdout=devnull, stderr=devnull,
                        shell=True)

        print(self.no_ext+'.arpa')
        #model creation be a separate thing (
        return os.path.abspath(self.no_ext+'.arpa')

    def decode(self, wavfile, offsets=False):
        '''
        Takes in a wavfile and returns an list of Annotations (see utils).
        :param wavfile:
        :param offsets:
        :return:
        '''

        devnull = open(os.devnull, 'w')
        starting_directory = os.path.dirname(wavfile)

        # create directories
        downsampled_8k_directory = os.path.join(os.path.dirname(wavfile), '8k_wavfiles/')
        self.dir_8k = downsampled_8k_directory
        if not os.path.exists(downsampled_8k_directory):
            os.makedirs(downsampled_8k_directory)

        # basenames etc
        base = os.path.basename(wavfile)
        self.no_ext = os.path.splitext(wavfile)[0]
        base_no_ext = os.path.splitext(base)[0]

        wavfile_8k = os.path.join(downsampled_8k_directory, base)
        utils.downsample(wavfile, wavfile_8k, 8000)
        self.wavfile_8k = wavfile_8k

        assert os.path.exists(wavfile_8k)
        raw_output = self._core_asr(wavfile_8k)
        self.kaldi_transcription = self._read_transcription(raw_output, offsets)
        return self.kaldi_transcription

    def _read_transcription(self, kaldi_output, offsets=False):
        '''
        Makes the output of Kaldi into an Annotation class or an AnnotationWithOffsets class
        :param kaldi_output:
        :param offsets:
        :return:
        '''
        kaldi_list = kaldi_output.decode("utf-8").split('\n')

        # This removes the first and last words since they're not actual words.
        filtered_kaldi_list = [x for x in kaldi_list if x.split(' ')[0] == 'utterance-id1']
        if filtered_kaldi_list:
            filtered_kaldi_list = filtered_kaldi_list[1:]

        if offsets == True:
            new_kaldi_output = [AnnotationWithOffsets(x.split(' ')[4], float(x.split(' ')[2]) * 1000,
                                                      float(x.split(' ')[2]) * 1000 + float(x.split(' ')[3]) * 1000) for x in
                                filtered_kaldi_list]
        else:
            new_kaldi_output = [Annotation(x.split(' ')[4], float(x.split(' ')[2]) * 1000) for x in filtered_kaldi_list]
        return new_kaldi_output

    def cleanup(self):
        '''Remove the folder after decoding is done, prevents Kaldi folder from getting too big.'''

        #Remove 8k_wavfiles
        try:
            shutil.rmtree(self.dir_8k)
        except OSError:
            pass

        if self.transcript_file.split('.')[-1] == '.transcript':
            #Remove .transcript
            try:
                os.remove(self.transcript_file)
            except OSError:
                pass

        #Remove .arpa
        try:
            os.remove(self.arpa)
        except OSError:
            pass

        #Remove Kaldi LM directory
        try:
            shutil.rmtree(self.tmp_directory)
        except OSError:
            pass

    def write_ann(self, annotation, dest, tmp_mode=False):
        word2numdict = pickle.load(open(self.word2numdict_path, 'rb'))
        # If tmp_mode, force manual review by creating .tmp instead of .ann
        outfile = dest + '.tmp' if tmp_mode else dest + '.ann'
        with open(outfile, 'w') as af:
            for pair in annotation:
                word = pair.word
                time = pair.time
                word_key = word.lower()
                if word_key in word2numdict:
                    word_num = word2numdict[word.lower()]
                else:
                    word_num = -1
                af.write('{}\t{}\t{}\n'.format(time, word_num, word))
    
    @staticmethod
    def write_oann(annotation, dest):
        with open(dest+'.oann', 'w') as af:
            for pair in annotation:
                onset = pair.onset
                word = pair.word.upper()
                offset = pair.offset
                af.write('{}\t{}\t{}\n'.format(onset, offset, word))


    def _core_asr(self, wavfile):
        '''This is where the speech recognition actually happens, call it from decode because otherwise the output is
        very messy. Takes in  a wavfile.'''

        new_base = os.path.join(self.loc, self.base)

        #we want to get the output but it returns a lot of logs
        output = subprocess.check_output('{0} {1} {2}'.format(self.ksl, new_base, wavfile),shell=True, stderr=subprocess.STDOUT)
        return output


if __name__ == "__main__":
    wavfile = sys.argv[1]
    lstfile = sys.argv[2]
    no_ext = lstfile.split('.')[0],
    config = '/home1/maint/speech_recognition_scripts/config.ini'
    kd = KaldiDecoder(lstfile, no_ext, config)
    kaldi_ann = kd.decode(wavfile)
    # kd.write_ann(kaldi_ann, no_ext)
    kd.cleanup()






