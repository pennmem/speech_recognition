from find_recently_modified import find_cont_subdir
import configparser
import sys
import os
from post_processing import post_process_directory
import datetime
import utils
import glob

def check_all_annotated_main_directory(session_folder, num_files):
    ann_files_to_check = [os.path.join(session_folder, str(num)+'.ann') for num in range(int(num_files))]
    if all([os.path.exists(x) for x in ann_files_to_check]):
        return True
    return False

def check_all_annotated_files_to_annotate(session_folder):
    wavfiles = glob.glob(os.path.join(session_folder, '/files_to_annotate/*.wav'))
    ann_files_to_check = [x.split('.')[0]+'.ann' for x in wavfiles]
    if all([os.path.exists(x) for x in ann_files_to_check]):
        return True
    return False

def check_annotated_files(single_word_files):
    if single_word_files:
        return check_all_annotated_main_directory
    else:
        return check_all_annotated_files_to_annotate

def main(config_file):
    '''
    Entry point of post-processing. This is meant to be called from recently_modified_postprocessing.sh
    '''

    global_config = configparser.ConfigParser()
    global_config.read(configfile)
    experiments = global_config.items('experiments')

    for experiment in experiments:
        exp_config_file = experiment[1]
        exp_config = configparser.ConfigParser()
        exp_config.read(exp_config_file)

        post_process=False
        try:
            post_process = exp_config['properties'].getboolean('post_process')
        except Exception:
            print("{} is missing some properties, please fix!".format(experiment))

        if post_process:

            try:
                exp_config = dict(exp_config.items('properties'))
                parse_files_root = exp_config['parse_files_root']
                log = exp_config['post_processing_log']
                post_processed_sessions = exp_config['post_processed_sessions']
                single_word_mode = bool(exp_config['single_word_files'])
            except Exception:
                print("{} is missing some properties, please fix!".format(experiment))
                raise

            rec_mod_sess = find_cont_subdir(parse_files_root, 'session')

            if not os.path.exists(post_processed_sessions):
                open(post_processed_sessions,'w').close()

            with open(post_processed_sessions) as fs:
                fin_sess_list = [x.rstrip('\n') for x in fs]

            if not os.path.exists(log):
                open(log,'w').close()

            now = datetime.datetime.now()
            sessions_to_annotate = [sess for sess in rec_mod_sess if sess not in fin_sess_list]

            with open(log, 'a') as l:
                l.write('Post-processing script ran on ' + now.strftime("%Y-%m-%d %H:%M") + '\n')
                l.write('The following sessions were found as needing post-processing:\n')
                for sess in sessions_to_annotate:
                    l.write('{}\n'.format(sess))

            for sess in sessions_to_annotate:
                if single_word_mode:
                    if check_all_annotated_main_directory(sess, exp_config['number_of_files']):
                        post_process_directory(sess, config_file, exp_config_file)
                        with open(post_processed_sessions,'a') as fd:
                            fd.write(sess + '\n')
                        with open(log, 'a') as l:
                            l.write('{} session {} was finished being post-processed. \n'
                            .format(utils.get_subject(sess),
                                    utils.get_session(sess)))
                    else:
                        with open(log,'a') as fd:
                            fd.write(sess + ' did not have all its files annotated, skipped. \n')
                else:
                    if check_all_annotated_files_to_annotate(sess):
                        post_process_directory(sess, config_file, exp_config_file)
                        with open(post_processed_sessions,'a') as fd:
                            fd.write(sess + '\n')
                        with open(log, 'a') as l:
                            l.write('{} session {} was finished being post-processed. \n'
                            .format(utils.get_subject(sess),
                                    utils.get_session(sess)))
                    else:
                        with open(log,'a') as fd:
                            fd.write(sess + ' did not have all its files annotated, skipped. \n')

if __name__ == '__main__':
    configfile = sys.argv[1]
    main(configfile)


