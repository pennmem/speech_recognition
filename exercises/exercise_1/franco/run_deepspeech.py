import sys

sys.path.append('/home1/maint/automatic_annotation/scripts/')
from deepspeech_decoder import DSDecoder
print(DSDecoder("session_0/0.lst", "0", '/home1/maint/automatic_annotation/config/config.ini').decode("session_0/0.wav"))
