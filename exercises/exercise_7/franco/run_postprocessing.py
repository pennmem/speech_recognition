import sys
sys.path.append('/home1/maint/automatic_annotation/scripts/')
from post_processing import post_process_file
config = '/home1/maint/automatic_annotation/config/config.ini'
exp_config = '/home1/maint/automatic_annotation/exercises/exercise_7/franco/exercise_7.ini'
post_process_file("/home1/maint/automatic_annotation/exercises/exercise_7/franco/session_0/0.wav",
               config, exp_config)
