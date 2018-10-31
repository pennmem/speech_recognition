from find_recently_modified import find_cont_subdir
import configparser
import sys
import os
from generate_ann import annotate_directory
import datetime
import utils

def main(config_file):
    '''
    Entry point of automatic annotation. This is meant to be called from asr_pipeline.sh
    '''

    global_config = configparser.ConfigParser()
    global_config.read(configfile)
    experiments = global_config.items('experiments')

    for experiment in experiments:
        exp_config_file = experiment[1]
        exp_config = configparser.ConfigParser()
        exp_config.read(exp_config_file)

        try:
            exp_config = dict(exp_config.items('properties'))
            root = exp_config['experiment_root']
            log = exp_config['log']
            finished_sessions = exp_config['finished_sessions']
        except Exception:
            print("{} is missing some properties, please fix!".format(experiment))

        rec_mod_sess = find_cont_subdir(root, 'session')

        if not os.path.exists(finished_sessions):
            open(finished_sessions,'w').close()

        with open(finished_sessions) as fs:
            fin_sess_list = [x.rstrip('\n') for x in fs]

        if not os.path.exists(log):
            open(log,'w').close()

        now = datetime.datetime.now()
        sessions_to_annotate = [sess for sess in rec_mod_sess if sess not in fin_sess_list]

        with open(log, 'a') as l:
            l.write('ASR script ran on ' + now.strftime("%Y-%m-%d %H:%M") + '\n')
            l.write('The following sessions were found as needing annotation:\n')
            for sess in sessions_to_annotate:
                l.write('{}\n'.format(sess))

        for sess in sessions_to_annotate:
            annotate_directory(sess, config_file, experiment)
            with open(finished_sessions,'a') as fd:
                fd.write(sess + '\n')
            with open(log, 'a') as l:
                l.write('{} session {} was finished being annotated. \n'
                        .format(utils.get_subject(sess),
                                utils.get_session(sess)))


if __name__ == '__main__':
    configfile = sys.argv[1]
    main(configfile)


