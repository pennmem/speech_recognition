# import deepspeech_decoder
import sys
import os
import glob
import utils, unk_handler, split_on_silence, single_word_annotate
from deepspeech_decoder import DSDecoder
from kaldi_align import KaldiDecoder

import configparser

KALDI_DIRECTORY = '/home1/maint/kaldi/egs/aspire/s5/'

def annotate_directory(start_directory, config_file, exp_config_file):
    '''
    Creates directories called 'files_to_annotate' which contains the files to be annotated and 'chunks' which contains
    wavfiles which are split on silence and no longer need to be annotated.
    :param start_directory:
    :return: None: writes files
    '''

    #Why do we do this instead of finding all wavfiles? Because it allows us to control which wavfiles are annotated,
    #which is useful for practice lists / ffr.
    exp_config = configparser.ConfigParser()
    exp_config.read(exp_config_file)

    num_files = int(exp_config['properties']['number_of_files'])

    files = glob.glob(os.path.join(start_directory, '*.wav')) + glob.glob(os.path.join(start_directory, '*.lst'))
    good_lists = []
    for x in range(num_files):
        if os.path.join(start_directory, str(x)+'.wav') in files and os.path.join(start_directory, str(x)+'.lst') in files:
            good_lists.append(x)

    for item in good_lists:
        wavfile = os.path.join(start_directory,str(item)+'.wav')
        lstfile = os.path.join(start_directory, str(item)+'.lst')
        annotate_file(wavfile, lstfile, config_file, exp_config_file)

def annotate_file(wavfile, lstfile, config_file, exp_config_file):
    '''
    This takes in a wavfile and splits it on silence before running a CTC based decoder (DeepSpeech) and then
    a WFST based decoder (Kaldi) on it. For each time '<unk>' is seen, we remove the preceding word and the succeeding
    word (see unk_handler for full description of logic), and make that a file for the annotator to annotate.

    :param wavfile: File containing audio
    :param lstfile: File containing expected words for list
    :return: Nothing, writes files to directory
    '''

    exp_config = configparser.ConfigParser()
    exp_config.read(exp_config_file)
    wordpool = exp_config['properties']['wordpool']


    if exp_config.getboolean('properties','single_word_files'):
        single_word_annotate.annotate(wavfile, lstfile, config_file, exp_config_file)

    else:
        #Downsampling to 16KHz needed for DeepSpeech
        utils.downsample(wavfile, wavfile, 16000)

        #Create Folders
        start_directory = os.path.dirname(wavfile)
        chunks_directory = os.path.join(start_directory, 'chunks/')
        files_to_annotate_directory = os.path.join(start_directory, 'files_to_annotate/')
        no_ext = os.path.splitext(wavfile)[0]

        if not os.path.exists(chunks_directory):
            os.makedirs(chunks_directory)

        if not os.path.exists(files_to_annotate_directory):
            os.makedirs(files_to_annotate_directory)

        #Creates DeepSpeech Model
        ds = DSDecoder(lstfile, no_ext, config_file)

        #First, we split the file on silence. This is helpful because CTC fails across large files and it also speeds up decoding.
        chunks = split_on_silence.split_on_silence(wavfile, chunks_directory)
        for chunk in chunks:
            #Runs DeepSpeech
            transcription = ds.decode(chunk.wavfile)
            ds.cleanup()
            if transcription:
                no_ext = os.path.splitext(chunk.wavfile)[0]
                #Runs Kaldi

                kd = KaldiDecoder(transcription, no_ext, config_file, wordpool)
                kaldi_ann = kd.decode(chunk.wavfile)
                kd.write_ann(kaldi_ann, no_ext)
                kd.cleanup()
                #Runs unknown handler
                if unk_handler.unk_in(kaldi_ann):
                    unk_handler.make_files_to_annotate(kaldi_ann, chunk.wavfile, files_to_annotate_directory, chunk.start_time, chunk.end_time)

    def create_transcript(transcription):
        '''
        Creates a .transcript file that contains all the words in words, separated by a newline. This needs to happen
        because the shell scripts need to run on files so we can't pass in word list.
        '''

        transcription_file = self.no_ext + '.transcript'
        with open(transcription_file, 'w') as tf:

            # the newline is needed for language model creation to work.
            tf.write(' '.join(transcript).upper() +'\n')
        return transcription_file


if __name__ == "__main__":
    wavfile = sys.argv[1]
    lstfile = sys.argv[2]
    annotate_file(wavfile, lstfile)


