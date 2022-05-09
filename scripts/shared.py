import  os
import audiofile as af
import sys
sys.path.append("./scripts")
import constant
from os.path import exists

def make_wav_cat(voc, emo, phrase, pi, index, path, play, out_file):
    """ generate a wav file.
        Args:
            voc: the Mbrola voice
            emo: the emotion name
            grade: the grade of the emotion
            phrase: the text that should be synthesized
            pi: the phrase index, for naming
            index: the index
            path: where to write the file
            play: whether to play back the file for control
            out_file: the list file to add the newly created wav file 
        Returns:
            the new index, incremented if wav file successfully created
    
    """
    name = f'{voc}_{emo}_p{str(pi).zfill(6)}'
    name += '.wav'
    cmd = f'python ./scripts/say_emo.py --emo {emo} --text \"{phrase}\" --voc {voc} \
        --wav {path}/{name}'
    if exists(f'{path}/{name}'):
        # if the file has been created on a previous occasion, use it
        print(f'skipping {path}/{name}')
        return index + 1
    if play:
        cmd += ' --play'
    os.system(cmd)
    sig, sr = af.read(path+name)
    if len(sig) < constant.MIN_LENGTH:
        """ There is quite a lot of stuff that might go wrong, emofilt has the tendency to make pho file unrenderable 
        (eg. when phonemes become too short or because of vowel target over/undershoot).
        Also MARY does not support all German voices properly, e.g. uses phonene symbols that are not part of the voice.
        So we simply ignore files that are too short or cause errors...
        """
        try:
            os.remove(path+name)
        except FileNotFoundError:
            pass
        with open(constant.ERROR_FILE, 'a') as ef:
            ef.write('ERROR  on file %s\n' % name)
        return index
    else:
        with open(out_file, 'a') as of:
            results = f'{path}{name},{voc},{constant.SEXES[voc]},{emo}\n'
            of.write(results)
        return index + 1

def make_wav_dim(voc, dir_a, grade_a, dir_v, grade_v, phrase, pi, index, path, play, out_file):
    """ generate a wav file.
        Args:
            voc: the Mbrola voice
            dir_a: the arousal emotion direction: high or low
            grade_a: the grade of the emotion
            dir_v: the valence emotion direction: high or low
            grade_v: the grade of the emotion
            phrase: the text that should be synthesized
            pi: the phrase index, for naming
            index: the index
            path: where to write the file
            play: whether to play back the file for control
            out_file: the list file to add the newly created wav file 
        Returns:
            the new index, incremented if wav file successfully created
    
    """
    # the two arousal dimensions
    arousals = constant.AROUSALS
    # the two valence dimensions
    valences= constant.VALENCES
    arousal = arousals[dir_a]
    valence = valences[dir_v]  
    # denote the direction of change  
    grade_a_n = -grade_a if dir_a == 'low' else grade_a
    grade_v_n = -grade_v if dir_a == 'low' else grade_v
    name = f'{voc}_p{str(pi).zfill(6)}_{grade_a_n:.3f}_{grade_v_n:.3f}'
    name += '.wav'
    cmd = f'python ./scripts/say_two_emo.py --emo1 {arousal} --grade1 {grade_a} '+\
        f'--emo2 {valence} --grade2 {grade_v} --text \"{phrase}\" --voc {voc} --wav {path}/{name}'
    if play:
        cmd += ' --play'
    os.system(cmd)
    sig, sr = af.read(path+name)
    if len(sig) < constant.MIN_LENGTH:
        """ There is quite a lot of stuff that might go wrong, emofilt has the tendency to make pho file unrenderable 
        (eg. when phonemes become too short or because of vowel target over/undershoot).
        Also MARY does not support all German voices properly, e.g. uses phonene symbols that are not part of the voice.
        So we simply ignore files that are too short or cause errors...
        """
        try:
            os.remove(name)
        except FileNotFoundError:
            pass
        with open(constant.ERROR_FILE, 'a') as ef:
            ef.write('ERROR  on file %s\n' % name)
        return index
    else:

        with open(out_file, 'a') as of:
            results = f'{path}{name},{voc},{constant.SEXES[voc]},{grade_a_n:.3f},{grade_v_n:.3f}\n'
            of.write(results)
        return index + 1
