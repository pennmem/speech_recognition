import os
import subprocess
from scripts import utils
import glob
import find_recently_modified

def check_all_exist(directory):
    '''
    Takes a directory and returns True if each ann file has a matching wavfile, False otherwise
    '''
    wavfiles = glob.glob(directory+'*.wav')
    annfiles = glob.glob(directory+'*.ann')
    wavfile_noext = set([os.splitext(f)[0] for f in wavfiles])
    annfiles_noext = set([os.splitext(f)[0] for f in wavfiles])
    if wavfile_noext == annfiles_noext:
        return True
    return False

def check_is_empty(annfile):
    '''
    Takes an annotation file and returns True is 'NA' is in the annotation
    '''
    annotation = utils.read_ann(annfile)
    if "NA" in annotation:
        return True
    return False

def write_par_file(annlist, dest):
    with open(dest,'w') as parf:
        for x in annlist:
            parf.write('{}\t{}\n'.format(x.word, x.time))

def email(subject, address):
    '''
    Wraps the bash utility, Python version doesn't work for me?
    '''
    subprocess.call('mail -s {} {}'.format(subject,address), shell=True)


def main():
    '''
    This is meant to be called from parsync.sh.
    '''

    rec_mod_dirs = find_recently_modified.find_cont_subdir('/home1/maint/parse_files/','session')

    for dir in rec_mod_dirs:

        #check if it has already been combined
        with open() as comb_sess:
            comb_sess_list = [x for x in comb_sess]

        if dir not in comb_sess_list:
            chunk_dir = os.path.join(dir, 'chunks/')
            fta_dir = os.path.join(dir, 'files_to_annotate/')

            #if it hasn't been combined, try to combine
            if check_all_exist(fta_dir):

                # in order to keep track of all the files, we look at the .times file - first, the one that shows the chunk files
                time_files = glob.glob(dir + '*.times')
                for tf in time_files:
                    base = os.path.basename(os.path.splitext(tf))
                    with open(tf) as time_list_file:
                        time_list = [x.rstrip('\n').split(' ')[0] for x in time_list_file]

                    #now, we can find the ann
                    for i, chunk_start in enumerate(time_list):
                        current_chunk_ann_file = os.path.join(chunk_dir, '{}_{}.ann'.format(chunk_start,i))
                        current_chunk_ann = utils.read_ann(current_chunk_ann_file)

                        current_chunk_time_file = os.path.join(chunk_dir, '{}_{}.times'.format(chunk_start,i))

                        #if the chunk file had unknown words then the file exists, otherwise it doesn't
                        if os.path.exists(current_chunk_time_file):
                            current_time_list = [x.rstrip('\n').split(' ')[0] for x in current_chunk_time_file]
                            current_end_time_list = [x.rstrip('\n').split(' ')[1] for x in current_chunk_time_file]

                            current_chunk_ann = [x for x in current_chunk_ann if x.time < ft]

                            #now, we remove the unks and surrounding words in the original ann file
                            unk_replacements = []

                            for i2, fta_start in enumerate(current_time_list):
                                #now, we find the user generated ann
                                fta_ann_file = '{}/{}_{}_{}.ann'.format(x, i, i2, fta_start)
                                if check_is_empty(fta_ann_file):
                                    pass
                                else:
                                    fta_ann = utils.read_ann(fta_ann_file)
                                    unk_replacements.extend(utils.add_ann(fta_ann, fta_start))

                            current_chunk_ann.extend(unk_replacements)
                        write_par_file(current_chunk_ann, os.path.join(dir, base+'.par'))
            else:
                email(r'Some files did not exist in {}, was not automatically combined.', 'francob@wharton.upenn.edu')

if __name__ == "__main__":
    main()
