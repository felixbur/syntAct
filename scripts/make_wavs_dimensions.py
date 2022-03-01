import  os
import audiofile as af
import audeer 
import argparse
import sys
sys.path.append("./scripts")
import constant

errorFile = './synth_errors.txt'


parser = argparse.ArgumentParser(description='Script to generate synthesized wav files from text.')
parser.add_argument('--texts', help='The texts file', required=True)
parser.add_argument('--wavs', help='The folder for the wav files', required=True)
parser.add_argument('--of', help='The output wave list', required=True)
parser.add_argument('--play', help='To play the wav files', action='store_true')

args = parser.parse_args()

with open(args.texts) as f:
    phrases = f.readlines()

out_file = args.of
play = args.play
wav_folder = args.wavs

phrases = [p.split('\t')[-1].strip() for p in phrases]

# maximum number of generate wav files
max_wave_num = 10000000
min_length = 500
index = 0
path = audeer.mkdir(wav_folder)+'/'

with open(out_file, 'a') as of:
    of.write('file,emotion,speaker,gender\n')

for vi, voc in enumerate(constant.VOICES):
   for pi, phrase in enumerate(phrases):
        for ei, emo in enumerate(constant.EMOTIONS):
            if index>max_wave_num:
                exit()
            name = f'{voc}_{emo}_p{str(pi).zfill(6)}.wav'
            cmd = f'python ./scripts/sayEmo.py --emo {emo} --text \"{phrase}\" --voc {voc} --wav {path}/{name}'
            if play:
                cmd += ' --play'
            os.system(cmd)
            sig, sr = af.read(path+name)
            if len(sig) < min_length:
                """ There is quite a lot of stuff that might go wrong, emofilt has the tendency to make pho file unrenderable 
                (eg. when phonemes become to shortn or because of vowel target over/undershoot).
                Also MARY does not support all German voices properly, e.g. uses phonene symbols that are not part of the voice.
                So we simply ignore files that are too short or cause errors...
                """
                try:
                    os.remove(name)
                except FileNotFoundError:
                    pass
                with open(errorFile, 'a') as ef:
                    ef.write('ERROR  on file %s\n' % name)
            else:
                index += 1
                with open(out_file, 'a') as of:
                    results = f'{path}{name},{emo},{voc},{constant.SEXES[voc]}\n'
                    of.write(results)
