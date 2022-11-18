"""
Python interface to the DFKI MARY text-to-speech synthesizer
based on https://github.com/marytts/marytts-txt2wav/blob/python/txt2wav.py

@author Felix Burkhardt
@copyright audEERING GmbH

"""
import httplib2
from urllib.parse import urlencode, quote # For URL creation
import os
import constants

class MarySynth():

    def __init__(self):
        # Mary server informations
        self.mary_host = "localhost"
        self.mary_port = "59125"
        # nothin to do: the MARY server must be started
        pass

    def synth(self, text, lang='en_US', gender=constants.GENDER_FEMALE, pleasure=.5,
              arousal=.5, dominance=.5, method='syntact',
              pitch_arousal=None, pitch_valence=None,
              pitch_dominance=None, pitch_interact=None,
              rate_arousal=None, rate_valence=None, rate_dominance=None,
              volume_arousal=None, volume_valence=None,
              volume_dominance=None):
        
        ssml = '<?xml version="1.0"?>\n'+\
        '<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\"\n'+\
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'+\
        ' xsi:schemaLocation="http://www.w3.org/2001/10/synthesis '+\
        'http://www.w3.org/TR/speech-synthesis/synthesis.xsd"\n'+\
        ' xml:lang="en-US">\n'+text+'\n</speak>'

        print(ssml)

        
        voices = {
            "de_DE": {
                "FEMALE": "dfki-poppy",
                "MALE": "dfki-obadiah"
            },
            "en_EN": {
                "FEMALE": "dfki-poppy",
                "MALE": "dfki-obadiah"
            },
            "en_US": {
                "FEMALE": "cmu-slt-hsmm",
                "MALE": "cmu-slt-hsmm"
            }
        }

        print("#####################")
        print(lang)
        print(gender)
        print(voices[lang][gender])
        print("#####################")
                       
        # Build the query
        query_hash = {"INPUT_TEXT": ssml,
                      "INPUT_TYPE": "SSML",
                      "LOCALE": lang,
                      "VOICE": voices[lang][gender], # Voice informations  (need to be compatible)
                      "OUTPUT_TYPE":"AUDIO",
                      "AUDIO":"WAVE",         # Audio informations (need both)
        }
        query = urlencode(query_hash)

        # Run the query to mary http server
        h_mary = httplib2.Http()
        resp, content = \
            h_mary.request(f'http://{self.mary_host}:{self.mary_port}/process?', 
                "POST", query)
        #  Decode the wav file or raise an exception if no wav files
        if (resp["content-type"] == "audio/x-wav"):
            return content
        else:
            raise Exception(content)

    def self_test(self):
        tmpfile = 'test.wav'
        text = 'Das ist mal ein deutscher Text.'
        # test_text = f'<prosody pitch="10%" rate="119%" volume="1dB">{text}</prosody>'
        audiosamples =  self.synth(text, lang="de_DE", gender="FEMALE")
        # The response's audio_content is binary.
        with open(tmpfile, "wb") as out:
            # Write the response to the output file.
            out.write(audiosamples)
        print(f'Audio content written to file {tmpfile}')

        os.system(f'play {tmpfile}')

if __name__ == "__main__":
    marysynth = MarySynth().self_test()
