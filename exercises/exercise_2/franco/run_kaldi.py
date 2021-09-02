import sys
sys.path.append('/home1/maint/automatic_annotation/scripts/')
import kaldi_align
print(kaldi_align(, "session_0/0.wav"))
    config = '/home1/maint/speech_recognition_scripts/config.ini'
    kd = KaldiDecoder("session_0/0.lst", "session_0/0", config)
    kaldi_ann = kd.decode(wavfile)
    kd.write_ann(kaldi_ann, no_ext)
    kd.cleanup()
