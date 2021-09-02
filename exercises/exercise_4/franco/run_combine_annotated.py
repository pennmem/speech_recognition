import sys
sys.path.append('/home1/maint/automatic_annotation/scripts/')
from combine_annotated_files import combine_main_directory_annotated_files
combine_main_directory_annotated_files("/home1/maint/automatic_annotation/exercises/exercise_4/franco/session_0/0.wav",
                                       "/home1/maint/automatic_annotation/wordpool_files/word2numdict.pickle")
