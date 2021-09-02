import sys
sys.path.append('/home1/maint/automatic_annotation/scripts/')
from kaldi_align import KaldiDecoder
config = '/home1/maint/speech_recognition_scripts/config.ini'
kd = KaldiDecoder("/home1/maint/automatic_annotation/exercises/exercise_2/franco/session_0/0.lst", "/home1/maint/automatic_annotation/exercises/exercise_2/franco/session_0/0", config)
kaldi_ann = kd.decode("/home1/maint/automatic_annotation/exercises/exercise_2/franco/session_0/0.wav")
kd.write_ann(kaldi_ann, "/home1/maint/automatic_annotation/exercises/exercise_2/franco/session_0/0")
