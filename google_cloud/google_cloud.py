from google.cloud import speech
import io
import sys
import pickle
import os
# from deepspeech_decoder import DSDecoder
# import configparser

subjects = [ u'R1063C', #u'R1375C', u'R1361C', u'R1123C', u'R1325C', u'R1364C', u'R1114C',
 u'R1122E', u'R1385E', u'R1057E', u'R1423E', u'R1433E', u'R1172E', u'R1161E',
 u'R1281E', u'R1275D', u'R1155D', u'R1104D', u'R1100D', u'R1166D', u'R1032D',
 u'R1154D', u'R1345D', u'R1401J', u'R1310J', u'R1049J', u'R1431J', u'R1191J',
 u'R1092J', u'R1081J', u'R1236J', u'R1131M', u'R1198M', u'R1031M', u'R1042M',
 u'R1324M', u'R1332M', u'R1412M', u'R1232N', u'R1142N', u'R1304N',
 u'R1118N', u'R1162N', u'R1175N', u'R1149N', u'R1250N', u'R1186P', u'R1067P',
 u'R1221P', u'R1003P', u'R1006P', u'R1066P', u'R1148P', u'R1089P', u'R1358T',
 u'R1125T', u'R1138T', u'R1077T', u'R1203T', u'R1113T' ]

def google_cloud_decode(wavfile, lstfile):
    client = speech.SpeechClient()
    with io.open(wavfile, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.types.RecognitionAudio(content=content)

    with open(lstfile) as lst_file:
        words = [x.strip().rstrip('\n').lower() for x in lst_file]
        print(words)

    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_word_time_offsets=True,
        sample_rate_hertz=44100,
        language_code='en-US',
        max_alternatives = 10,
        speech_contexts=[speech.types.SpeechContext(phrases=words)])

    response = client.recognize(config, audio)
    return response

if __name__ =='__main__':
    subj = sys.argv[1]
    file = sys.argv[2]
    print(google_cloud_decode('/data/eeg/{}/behavioral/FR1/session_0/{}.wav'.format(subj, file),
                              '/data/eeg/{}/behavioral/FR1/session_0/{}.lst'.format(subj, file)))



