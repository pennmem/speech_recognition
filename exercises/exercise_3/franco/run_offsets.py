import sys
sys.path.append('/home1/maint/automatic_annotation/scripts/')
from offsets_align import create_offsets
config = '/home1/maint/automatic_annotation/config/config.ini'
create_offsets("/home1/maint/automatic_annotation/exercises/exercise_3/franco/session_0/0.wav",
               "/home1/maint/automatic_annotation/exercises/exercise_3/franco/session_0/0.lst",
               "/home1/maint/automatic_annotation/exercises/exercise_3/franco/session_0/0.ann",
               config)
