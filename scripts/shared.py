import  os
import audiofile as af
import sys
sys.path.append("./scripts")
import constant

def make_wav(voc, emo, grade, phrase, pi, index, path, play, out_file):
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
    if grade != -1:
        name += f'_{grade:.3f}'
    name += '.wav'
    cmd = f'python ./scripts/sayEmo.py --emo {emo} --text \"{phrase}\" --voc {voc} \
        --grade {grade} --wav {path}/{name}'
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
            results = f'{path}{name},{emo},{voc},{constant.SEXES[voc]},{grade:.3f}\n'
            of.write(results)
        return index + 1
