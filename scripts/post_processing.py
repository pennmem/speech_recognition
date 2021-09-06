import os
import glob
import offsets_align

import configparser

def post_process_directory(start_directory, config_file, exp_config_file):
    '''
    :param start_directory:
    :param config_file:
    :param exp_config_file:
    :return: None: writes files
    '''

    #Why do we do this instead of finding all wavfiles? Because it allows us to control which wavfiles are annotated,
    #which is useful for practice lists / ffr.
    exp_config = configparser.ConfigParser()
    exp_config.read(exp_config_file)

    files = glob.glob(os.path.join(start_directory, '*.wav'))

    for f in files:
        post_process_file(f, config_file, exp_config_file)

def post_process_file(wavfile, config_file, exp_config_file, tmp_mode=False):
    '''
    This takes in a wavfile and depending on whether or not it is a
    :param wavfile: File containing audio
    :return: Nothing, writes files to directory
    '''

    exp_config = configparser.ConfigParser()
    exp_config.read(exp_config_file)

    config = configparser.ConfigParser()
    config.read(config_file)
    print(config.sections())

    base_name = wavfile.split('.')[0]
    lstfile = base_name + '.lst'
    annfile = base_name + '.tmp' if tmp_mode else base_name + '.ann'
    
    offsets_align.create_offsets(wavfile, lstfile, annfile, config_file)
