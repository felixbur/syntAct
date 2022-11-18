"""
Python methods to synthesize a given text based on Google services

@author Felix Burkhardt, Uwe Reichel
@copyright audEERING GmbH

"""

from datetime import datetime
from io import BytesIO
import os
import re

from google.cloud import texttospeech
import json
import librosa
import numpy as np

import audeer
import audiofile as af
from emosimulator import Emosimlator
import constants
from espeaksynth import EspeakSynth
from marysynth import MarySynth

class Textsynth():
    
    def __init__(self):
        print('preparing text to speech...')
        # set up the Google Speech API key
        cwd = os.path.dirname(os.path.abspath(__file__))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
            os.path.join(cwd, "..", "easier-329810-57e26fbe7ac0.json")

        # Instantiates a client
        self.client = texttospeech.TextToSpeechClient()

        # Select the type of audio file you want returned
        self.audio_config = texttospeech.AudioConfig(
            sample_rate_hertz=16000,
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        self.emosimlator = Emosimlator()
        self.marysynth = MarySynth()
        self.espeaksynth = EspeakSynth()
        print('preparing text to speech done')
            
        
    def synth(self, text, lang, gender, pleasure,
              arousal, dominance, method='syntact',
              pitch_arousal=None, pitch_valence=None,
              pitch_dominance=None, pitch_interact=None,
              rate_arousal=None, rate_valence=None, rate_dominance=None,
              volume_arousal=None, volume_valence=None,
              volume_dominance=None):
        
        """Synthesizes speech from the input string of text or ssml.
            Make sure to be working in a virtual environment.
            Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        """
        
        # check whether monthly limit is reached
        # if so, use espeak
        cwd = os.path.dirname(os.path.abspath(__file__))
        f_cnt = os.path.join(cwd, "counter", "counter_tts.json")
        with open(f_cnt, "r") as h:
            cnt = json.load(h)

        today = datetime.today().date()
        this_month = re.sub("\-\d\d$", "", str(today))
        if this_month not in cnt:
            cnt[this_month] = 0
        add_estimate = len(text) * 2
        newcount = cnt[this_month] + add_estimate

        # update cnt only if special key is used
        if newcount > cnt["limit"]:

            # espeak: not yet working, cannot properly convert np.ndarray to byte array
            # return self.espeaksynth(text, lang=lang, gender=gender, pleasure=pleasure,
            #                         arousal=arousal, dominance=dominance)
            
            # mary TTS
            return self.marysynth.synth(
                text,
                lang=lang,
                gender=gender,
                pleasure=pleasure,
                arousal=arousal,
                dominance=dominance,
                method=method
            )
        
        ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL
        if gender.lower() == constants.GENDER_FEMALE.lower():
            ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
        elif gender.lower() == constants.GENDER_MALE.lower():
            ssml_gender = texttospeech.SsmlVoiceGender.MALE
        else:
            print(f'ERROR: unkown gender: {gender}')

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=lang, ssml_gender=ssml_gender
        )
        
        if method == "syntact":
            method = constants.METHOD_SYNTACT
        elif method == "schroeder":
            method = constants.METHOD_SCHROEDER
        elif method == "avd":
            method = constants.METHOD_AVD
        elif method == "none":
            method = constants.METHOD_PASS
        else:
            print(f'ERROR: unkown method: {method}')
        
        # emotionalize the input
        # method = 'na'
        text = self.emosimlator.emotionalize(method, text, pleasure,
                                             arousal, dominance, lang,
                                             pitch_arousal, pitch_valence,
                                             pitch_dominance, pitch_interact,
                                             rate_arousal, rate_valence,
                                             rate_dominance,
                                             volume_arousal, volume_valence,
                                             volume_dominance)

        # print(f'got \"{text}\"')

        # update cnt and write back to json
        cnt[this_month] += len(text)
        with open(f_cnt, "w") as h:
            json.dump(cnt, h, indent="  ", sort_keys=True)
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(ssml=text)

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=self.voice,
            audio_config=self.audio_config
        )
        
        return response.audio_content

    def self_test(self):
        tmpfile = 'xyz.wav'
        test_text = 'Und das ist mal ein anderes Beispiel.'
        # test_text = '<speak><prosody pitch="80%" rate="119%" volume="1dB">Und das ist mal ein anderes Beispiel.</prosody></speak>'
        # test_text = '<speak><prosody pitch="-50%" rate="50%" volume="10dB">Und das ist mal ein anderes Beispiel.</prosody></speak>'
        # test_text = '<speak><prosody rate="150%">Und das ist mal ein anderes Beispiel.</prosody></speak>'
        # test_text = '<speak><prosody pitch="30%">Und das ist mal ein anderes Beispiel.</prosody></speak>'
        # test_text = '<speak><prosody volume="-20dB">Und das ist mal ein anderes Beispiel.</prosody></speak>'
        # test_text = '<speak><prosody pitch="+30%" rate="140%">Und das ist mal ein anderes Beispiel.</prosody></speak>'
        
        audiosamples = self.synth(test_text, 'de_DE', constants.GENDER_MALE, .2, .4, .5,
                                  method=constants.METHOD_SYNTACT)

        if type(audiosamples) is np.ndarray:
            # espeak output
            af.write(tmpfile, audiosamples, 16000)
        else:
            # google tts output
            # The response's audio_content is binary.
            with open(tmpfile, "wb") as out:
                # Write the response to the output file.
                out.write(audiosamples)
            print(f'Audio content written to file {tmpfile}')

        os.system(f'play {tmpfile}')

if __name__ == "__main__":
    Textsynth().self_test()
