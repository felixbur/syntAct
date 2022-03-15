from sqlite3 import adapt
import audiofile as af
import audeer 
import argparse
import sys
sys.path.append("./scripts")
import constant
import shared 
import random
import numpy as np

# error messages should go here
error_file = './synth_errors.txt'


parser = argparse.ArgumentParser(description='Script to generate synthesized wav files from text.')
parser.add_argument('--texts', help='The texts file', required=True)
parser.add_argument('--num', help='The number of wav files to be synthesized', required=True)
parser.add_argument('--wavs', help='The folder for the wav files', default='synthesized_audio')
parser.add_argument('--of', help='The output wave list', default='synth_out.csv')
parser.add_argument('--play', help='To play the wav files', action='store_true')

args = parser.parse_args()

with open(args.texts) as f:
    phrases = f.readlines()

out_file = args.of
play = args.play
wav_folder = args.wavs
num = int(args.num)

phrases = [p.split('\t')[-1].strip() for p in phrases]

# maximum number of generated wav files
max_wave_num = num
# minimum sensible length for wav file
min_length = constant.MIN_LENGTH
index = 0
phrase_index = 0
path = audeer.mkdir(wav_folder)+'/'

with open(out_file, 'a') as of:
    of.write('file,emotion,speaker,gender,arousal,valence\n')


# the available voices
voices = constant.VOICES

with open(out_file, 'a') as of:
    of.write('file,speaker,gender,arousal,valence\n')

while index<max_wave_num:
    for vi, voc in enumerate(constant.VOICES):
        phrase = phrases[phrase_index]
        # arousal goes in direction high or low
        a_direction = random.choice(['high', 'low'])
        # valence goes in direction high or low
        v_direction = random.choice(['high', 'low'])
        grades = np.random.normal(.5, .3, 2)
        grade_a = grades[0]
        grade_v = grades[1]
        index = shared.make_wav_dim(voc, a_direction, grade_a, v_direction, grade_v, phrase, phrase_index, index, path, play, out_file)
        phrase_index += 1



    # step_index = pi % len(steps)
    # dim_index = int(pi / len(steps))
