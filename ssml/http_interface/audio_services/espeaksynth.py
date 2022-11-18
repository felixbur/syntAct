import os

import numpy as np
import librosa
import audeer
import audiofile as af
import constants
from emosimulator import Emosimlator

class EspeakSynth():

    def __init__(self):

        self.emosimlator = Emosimlator()

    def synth(self, text, lang, gender, pleasure,
              arousal, dominance,
              pitch_arousal=0.0, pitch_valence=0.0,
              pitch_dominance=0.0, pitch_interact=1,
              rate_arousal=0.0, rate_valence=0.0, rate_dominance=0.0,
              volume_arousal=0.0, volume_valence=0.0,
              volume_dominance=0.0, verbose=False):

        ''' fallback TTS using espeak
        Args:
        text: (str) text to be synthesized
        lang: (str) language de-DE, en-EN, etc
        gender: (str) FEMALE, MALE
        pleasure, arousal, dominance: (float) between 0 and 1
        pitch_*: factors mapping pleasure, arousal, dominance values
               to pitch modification factors
        pitch_interact: (float) set to -1 if dominance and arousal
            should interact in pitch modification. Set to 1, if not
        rate_*: factors mapping pleasure, arousal, dominance values
               to rate modification factors
        volume_*: factors mapping pleasure, arousal, dominance values
               to energy modification factors
        verbose: (boolean) +/-verbose
        Returns:
        signal: (np.array) 16kHz mono signal

        Details: http://espeak.sourceforge.net
        '''

        # select voice
        # see https://github.com/numediart/MBROLA-voices
        # no female voice for English
        voimap = {
            "de-DE": {
                "FEMALE": "de7",
                "MALE": "de6"
            },
            "en-EN": {
                "FEMALE": "de7",
                "MALE": "en1"
            },
            "other": {
                "FEMALE": "de7",
                "MALE": "de6"
            }
        }
        gender = gender.upper()
        if lang not in voimap:
            lang = "other"
        voice = voimap[lang][gender]

        # SSML prosody modification factors
        kwargs = {"method": constants.METHOD_AVD,
                  "text": text,
                  "pleasure": pleasure,
                  "arousal": arousal,
                  "dominance": dominance,
                  "language": lang,
                  "pitch_arousal": pitch_arousal,
                  "pitch_valence": pitch_valence,
                  "pitch_dominance": pitch_dominance,
                  "pitch_interact": pitch_interact,
                  "rate_arousal": rate_arousal,
                  "rate_valence": rate_valence,
                  "rate_dominance": rate_dominance,
                  "volume_arousal": volume_arousal,
                  "volume_valence": volume_valence,
                  "volume_dominance": volume_dominance,
                  "return_type": "values"}
        pmf = self.emosimlator.emotionalize(**kwargs)
        
        if verbose:
            print("SSML parameters:", pmf)

        # convert to easpeak parameters
        pitch, rate, volume = self.convert_ssml_easier(**pmf)
        
        # write TTS output into tmp file (with unique name)
        cwd = os.path.dirname(os.path.abspath(__file__))
        tmp_dir = os.path.join(cwd, "tmp")
        _ = audeer.mkdir(tmp_dir)
        tmp = os.path.join(tmp_dir, f"tmp_{os.getpid()}.wav")

        cmd = f"espeak -vmb-{voice} -p {pitch} -s {rate} -a {volume} \"{text}\" -w {tmp}"

        os.system(cmd)

        if verbose:
            print("command:", cmd)
            os.system(f"aplay {tmp}")
        
        # read, resample
        sr = 16000
        signal, sampling_rate = af.read(tmp)
        if sampling_rate != sr:
            signal = librosa.resample(signal, orig_sr=sampling_rate,
                                      target_sr=sr)

        # clean up
        if os.path.isfile(tmp):
            os.remove(tmp)
            
        return signal

    
    def convert_ssml_easier(self, pitch, rate, volume):

        ''' maps prosody modif factors to espeak-specific ranges
        why this workaround? espeak cannot interprete the pitch attribute in the SSML, so that we need
        to call it with -p|s|a attributes
        SSML: <prosody pitch="0%" rate="100%" volume="0dB">
        espeak ranges and default values:
        pitch ([0 99], <50>)     no unit
        rate  ([80 450], <175>)  words per minute
        volume ([0 200], <100>)  no unit (amplitude)

        Args:
        pitch, rate, volume: (floats) SSML prosody values
        Returns:
        epitch, erate, evolume: (floats) espeak prosody values
        '''

        # pitch value describes relative change
        epitch = 50 + (50 * pitch / 100)

        # rate value describes proportion
        erate = 175 * rate / 100
        
        # volume values describes change in dB
        # 20*log10(p1/p0), p0=100, resolve for p1
        evolume = 20 * 10**volume * 100

        # ensure limits
        def limit(x, b1, b2):
            return min(max(x, b1), b2)

        # limit values chosen so that audio is still audible
        epitch = limit(epitch, 15, 99) # 80 90
        erate = limit(erate, 80, 400)  # 250 260 320
        evolume = limit(evolume, 30, 200) # 200

        return epitch, erate, evolume
    
    
    def rescale(self, x, oldmin, oldmax, newmin, newmax):
        
        oldrange = oldmax - oldmin
        newrange = newmax - newmin
        return (((x - oldmin) * newrange) / oldrange) + newmin

    
    def rescale_imbalanced(self, x, oldmin, oldmax, newmin, newmid, newmax):
        
        oldmid = oldmin + (oldmax - oldmin) / 2
        if x <= oldmid:
            return self.rescale(x, oldmin, oldmid, newmin, newmid)
        else:
            return self.rescale(x, oldmid, oldmax, newmid, newmax)
