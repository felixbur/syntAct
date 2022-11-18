"""
Python methods to simulate emotional arousal for speech synthesis based on SSML tags.

@author Felix Burkhardt, Uwe Reichel
@copyright audEERING GmbH

possiblities with SSML:
    <emphasis level="moderate | strong">
    <prosody rate, pitch, volume>

pleasure, arousal, dominance range from 0 to 1, with .5 being the neutral state

changes to pitch, rate, volume  will be given in percentage

"""

# import constants_alternative as constants
import constants
import spacy

class Emosimlator():
    """Class to emotionalize a speech input using SSML tags."""

    def __init__(self):
        self.min=0
        self.max=1

    def rescale(self, input, min, max, newmin, newmax):
        # a rescaler for measures where the neutral value is not in the middle
        oldrange = max - min
        newrange = newmax - newmin
        return (((input - min) * newrange) / oldrange) + newmin

    def rescale_imbalanced(self, input, min, max, newmin, newmid, newmax):
        oldmid = min + (max-min) / 2
        if input <= oldmid:
            return self.rescale(input, min, oldmid, newmin, newmid)
        else:
            zz = self.rescale(input, oldmid, max, newmid, newmax) #!x
            return self.rescale(input, oldmid, max, newmid, newmax)

    def emotionalize(self, method, text, pleasure, arousal, dominance,
                     language="de_DE", pitch_arousal=None, pitch_valence=None,
                     pitch_dominance=None, pitch_interact=None,
                     rate_arousal=None, rate_valence=None, rate_dominance=None,
                     volume_arousal=None, volume_valence=None,
                     volume_dominance=None,
                     min_pitch=constants.MIN_PITCH,
                     mid_pitch=constants.MID_PITCH,
                     max_pitch=constants.MAX_PITCH,
                     min_rate=constants.MIN_RATE,
                     mid_rate=constants.MID_RATE,
                     max_rate=constants.MAX_RATE,
                     min_volume=constants.MIN_VOLUME,
                     mid_volume=constants.MID_VOLUME,
                     max_volume=constants.MAX_VOLUME,
                     return_type="ssml"):

        ''' generates SSML with elements to emotionalize TTS
        Args:
        method: (str) SSML generation method; "schroeder", "syntact", "avd", "none"
        text: (str) text to be marked up
        pleasure, arousal, dominance: (float) emotion scores in [0, 1]
        language: (str) language: "de_DE", "en_EN", ...
        pitch_*: (floats) emotion weights for pitch
        pitch_interact: (float) set to -1 if dominance and arousal should interact
            in pitch modification. Set to 1, if not
        rate_*: (floats) emotion weights for speaking rate
        volume_*: (floats) emotion weights for energy
        min|mid|max_pitch|rate|volume: (floats) min, default, and max value of modification
             of pitch, rate, and volume (as shown in SSML prosody attributes)
        return_type: (str) "ssml" or "values" (see Returns)
        Returns:
        if return_type is "ssml": text with SSML markup
        if return_type is "values": dict with keys "pitch", "rate", and "volume" 

        For all weights there are method-dependent defaults.
        '''
        
        # initializations
        pitch, rate, volume = \
            constants.NEUTRAL_PITCH, \
                constants.NEUTRAL_RATE, \
                    constants.NEUTRAL_VOLUME

        # rescale to [-1, 1]
        pleasure = self.rescale(pleasure, 0, 1, -1, 1)
        arousal = self.rescale(arousal, 0, 1, -1, 1)
        dominance = self.rescale(dominance, 0, 1, -1, 1)

        if method == constants.METHOD_PASS:
            # just don't do anything

            return text

        elif method == constants.METHOD_SCHROEDER:

            if not pitch_arousal:
                pitch_arousal = .75
            if not pitch_valence:
                pitch_valence = .25
            
            # compute the pitch factor
            # Version 0.1: we shift pitch upwards according to positive arousal nd lower for negative
            # ... pitchShift = int(rescale(arousal, min, max, 0.5, 1.5) * 100)
            # According to Schroeder, `pitch => 0.3 * activation + 0.1 * evaluation - 0.1 * power
            # we first scale from -1 to 1 
            pitch = pitch_arousal * arousal + pitch_valence * pleasure
            pitch = self.rescale_imbalanced(pitch, -1, 1, min_pitch,
                                            mid_pitch, max_pitch)

            if not rate_arousal:
                rate_arousal = .66
            if not rate_valence:
                rate_valence = .33
            
            # Version 01: we lower the speech rate with valence
            # ... speechRateShift = int(rescale(valence, min, max, 0.5, 1.5) * 100)
            # According to Schroeder, `rate => 0.5 * activation + 0.2 * evaluation`
            # we first scale from -1 to 1 
            rate = rate_arousal * arousal + rate_valence * pleasure
            rate = self.rescale_imbalanced(rate, -1, 1, min_rate,
                                           mid_rate, max_rate)

            # We set the volume factor simply in relation to arousal
            if not volume_arousal:
                volume_arousal = 1.0
            if not volume_valence:
                volume_valence = 0.0

            volume = volume_arousal * arousal + volume_valence * pleasure
            volume = self.rescale_imbalanced(volume, -1, 1, min_volume,
                                             mid_volume, max_volume)

            # print(f'returning {pitch:.3f} {rate:.3f} {volume:.3f}')

            if return_type == "values":
                return {"pitch": pitch,
                        "rate": rate,
                        "volume": volume}
            
            # add the SSML tags
            text = f'<speak><prosody '+\
                f'pitch=\"{int(pitch)}%\" '+\
                f'rate=\"{int(rate)}%\" '+\
                f'volume=\"{int(volume)}dB\"'+\
                f'>{text}</prosody></speak>'

        elif method == constants.METHOD_SYNTACT:

            if not pitch_arousal:
                pitch_arousal = 0.0
            if not pitch_valence:
                pitch_valence = 1.0
            
            # compute the pitch factor
            # According to syntact, pitch is only influenced by valence
            # we first scale from -1 to 1 
            pitch = pitch_arousal * arousal + pitch_valence * pleasure
            pitch = self.rescale_imbalanced(pitch, -1, 1, min_pitch,
                                            mid_pitch, max_pitch)

            if not rate_arousal:
                rate_arousal = 1.0
            if not rate_valence:
                rate_valence = 0.0
            
            # Version 01: we lower the speech rate with valence
            # According to syntact, speech rate is only influenced by arousal
            # we first scale from -1 to 1 
            rate = rate_arousal * arousal + rate_valence * pleasure
            rate = self.rescale_imbalanced(rate, -1, 1, min_rate,
                                           mid_rate, max_rate)

            # We set the volume factor simply in relation to arousal
            if not volume_arousal:
                volume_arousal = 1.0
            if not volume_valence:
                volume_valence = 0.0

            volume = volume_arousal * arousal + volume_valence * pleasure
            volume = self.rescale_imbalanced(volume, -1, 1, min_volume,
                                             mid_volume, max_volume)

            # print(f'returning {pitch:.3f} {rate:.3f} {volume:.3f}')

            if return_type == "values":
                return {"pitch": pitch,
                        "rate": rate,
                        "volume": volume}
            
            # add the SSML tags
            text = f'<speak><prosody '+\
                f'pitch=\"{int(pitch)}%\" '+\
                f'rate=\"{int(rate)}%\" '+\
                f'volume=\"{int(volume)}dB\"'+\
                f'>{text}</prosody></speak>'

        elif method == constants.METHOD_AVD:

            # make ranges narrower
            min_pitch=-10
            mid_pitch=0
            max_pitch=20
            min_rate=70
            mid_rate=100
            max_rate=200
            min_volume=-10
            mid_volume=0
            max_volume=20

            # pitch
            if not pitch_arousal:
                pitch_arousal = 0.5 # .1
            if not pitch_valence:
                pitch_valence = -.5 # .1
            if not pitch_dominance:
                pitch_dominance = -.2  # -.4
            # pitch_interact accounts for arousal/dominance interaction
            # best set to -1 (interaction) or 1 (no interaction)
            if not pitch_interact:
                pitch_interact = 1 # -1
                
            # interaction arousal/dominance
            if dominance >= .5:
                pitch_arousal *= pitch_interact
                
            pitch = pitch_arousal * arousal + pitch_valence * pleasure + pitch_dominance * dominance
            pitch = self.rescale_imbalanced(pitch, -1, 1, min_pitch,
                                            mid_pitch, max_pitch)

            # speaking rate
            if not rate_arousal:
                rate_arousal = .9 # .7
            if not rate_valence:
                rate_valence = .5 # .1
            if not rate_dominance:
                rate_dominance = .5 # -.2

            rate = rate_arousal * arousal + rate_valence * pleasure + rate_dominance * dominance
            rate = self.rescale_imbalanced(rate, -1, 1, min_rate,
                                           mid_rate, max_rate)
            
            # energy
            if not volume_arousal:
                volume_arousal = .8 # .7
            if not volume_valence:
                volume_valence = -.5 # -.1
            if not volume_dominance:
                volume_dominance = .7 # .2
            
            volume = volume_arousal * arousal + volume_valence * pleasure + volume_dominance * dominance
            volume = self.rescale_imbalanced(volume, -1, 1, min_volume, mid_volume, max_volume)

            # print(f'returning {pitch:.3f} {rate:.3f} {volume:.3f}')

            if return_type == "values":
                return {"pitch": pitch,
                        "rate": rate,
                        "volume": volume}
            
            tag_left = f'<speak><prosody pitch=\"{int(pitch)}%\" rate=\"{int(rate)}%\" volume=\"{int(volume)}dB\">'
            tag_right = '</prosody></speak>'

            # emphasis of nouns and adjectives
            #     - for above average arousal ("moderate", "strong")
            #     - for very low arousal ("reduced")
            level = None
            if arousal >= .5 or dominance >= .5:
                level = "strong"
            elif arousal >= .0:
                level = "moderate"
            elif arousal < -.5:
                level = "reduced"
            #elif valence > .5:
            #    level = "moderate"

            # nothing to be emphasized
            if ((level is None) or (language not in ["de_DE", "en_US"])):
                return f"{tag_left}{text}{tag_right}"

            # POS tagging
            if language == "de_DE":
                nlp = spacy.load("de_core_news_sm")
                self.nlp = spacy.load("de_core_news_sm")
            elif language == "en_US":
                nlp = spacy.load("en_core_web_sm")

            tokens = []
            doc = nlp(text)            
            for token in doc:
                tok = token.text
                pos = token.pos_
                # print(tok, pos)
                if pos in ["NOUN", "ADJ", "ADV"]:
                    tokens.append(f"<emphasis level=\"{level}\">{tok}</emphasis>")
                else:
                    tokens.append(tok)

            text = " ".join(tokens)
            
            return f"{tag_left}{text}{tag_right}"

        else:
            print(f'ERROR: unkown method: {method}')
            
        # return fallback
        return f"<speak>{text}</speak>"

