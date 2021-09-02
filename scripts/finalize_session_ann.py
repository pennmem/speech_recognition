import os
import pickle
import utils
import configparser
import sys
from combine_annotated_files import combine_main_directory_annotated_files

#def combine_all_wav(session_dir, exp_config_file, ffr = True):
session_dir = sys.argv[1]
exp_config_file = sys.argv[2]
ffr = sys.argv[3]
exp_config = configparser.ConfigParser()
exp_config.read(exp_config_file)
num_files = int(exp_config['properties']['number_of_files'])
if ffr == 'true':
    num_files += 1

	#Create pickled wordpool dictionary here.
	#Note: the config file in config.ini takes in a wordpool dict, so I'm not sure what else 
	#we would want to change throughout the code if we use what's below to create the dictionary

wordpool = exp_config['properties']['wordpool']
wordpool_list= [x.rstrip('\n') for x in open(wordpool)]
value_list = list(range(len(wordpool_list) + 1))
wordpool_dict = dict(zip(wordpool_list, value_list))
pickle_wordpool = open('wordpool.pickle', 'wb')
pickle.dump(wordpool_dict, pickle_wordpool)
pickle_wordpool.close()

	#combine_main_directory_annotated_files expects a filepath to pickled wordpool dict.
	#I think I coded it so it will save in the working directory? 

for i in list(range(num_files)):
    if (i == num_files - 1) & (ffr == 'true'):
        base_name = os.path.join(session_dir, 'ffr')
        wavfile = base_name + '.wav'
        combine_main_directory_annotated_files(wavfile, '/home1/maint/automatic_annotation/wordpool_files/RepFR_wordpool.pickle')
        continue
    else:
        base_name = os.path.join(session_dir, str(i))
        wavfile = base_name + '.wav'
        combine_main_directory_annotated_files(wavfile, '/home1/maint/automatic_annotation/wordpool_files/RepFR_wordpool.pickle')	
