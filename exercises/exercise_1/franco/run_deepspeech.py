import sys
import deepspeech_decoder
sys.path.append('/home1/maint/automatic_annotation/scripts/')
print(deepspeech_decoder.decode("session_0/0.lst", "session_0/0.wav"))