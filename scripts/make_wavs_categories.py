import  os
import audiofile as af
import audeer 
import argparse
import sys
sys.path.append("./scripts")
import constant
import shared 
import numpy as np

# error messages should go here
error_file = './synth_errors.txt'


parser = argparse.ArgumentParser(description='Script to generate synthesized wav files from text.')
parser.add_argument('--texts', help='The texts file', required=True)
parser.add_argument('--wavs', help='The folder for the wav files', required=True)
parser.add_argument('--of', help='The output wave list', required=True)
parser.add_argument('--change_phrase', help='Whether the emotions get different phrases or each\
     phrase in all emotions', action='store_true')
parser.add_argument('--play', help='To play the wav files', action='store_true')
parser.add_argument('--grades', help='Whether grades should be used', action='store_true')
parser.add_argument('--random_grade', help='Whether grades should be randomly distributed', action='store_true')

args = parser.parse_args()

with open(args.texts) as f:
    phrases = f.readlines()

out_file = args.of
play = args.play
wav_folder = args.wavs

phrases = [p.split('\t')[-1].strip() for p in phrases]

# maximum number of generate wav files
max_wave_num = 100000
min_length = 500
index = 0
path = audeer.mkdir(wav_folder)+'/'

with open(out_file, 'a') as of:
    of.write('file,emotion,speaker,gender\n')

# our set of categorical emotions
emotions = constant.EMOTIONS
if args.change_phrase:
    for vi, voc in enumerate(constant.VOICES):
        for pi, phrase in enumerate(phrases):
            if index>max_wave_num:
                exit()
            emo_index = pi % len(emotions)-1
            emo = emotions[emo_index]
            index = shared.make_wav(voc, emo, -1, phrase, pi, index, path, play)
else:
    for vi, voc in enumerate(constant.VOICES):
        for pi, phrase in enumerate(phrases):
            for ei, emo in enumerate(constant.EMOTIONS):
                if index>max_wave_num:
                    exit()
                index = shared.make_wav(voc, emo, -1, phrase, pi, index, path, play)
