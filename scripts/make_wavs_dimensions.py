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
parser.add_argument('--wavs', help='The folder for the wav files', default='synthesized_audio')
parser.add_argument('--of', help='The output wave list', default='synth_out.csv')
parser.add_argument('--change_phrase', help='Whether the emotions get different phrases or each\
     phrase in all emotions', action='store_true')
parser.add_argument('--play', help='To play the wav files', action='store_true')
parser.add_argument('--random_grade', help='Whether grades should be randomly distributed or be fixed', action='store_true')

args = parser.parse_args()

with open(args.texts) as f:
    phrases = f.readlines()

out_file = args.of
play = args.play
wav_folder = args.wavs

phrases = [p.split('\t')[-1].strip() for p in phrases]

# maximum number of generate wav files
max_wave_num = 20
min_length = 500
index = 0
path = audeer.mkdir(wav_folder)+'/'

with open(out_file, 'a') as of:
    of.write('file,emotion,speaker,gender,intensity\n')

steps = [0, .33, .66, 1]

if args.change_phrase:
    for vi, voc in enumerate(constant.VOICES):
        for pi, phrase in enumerate(phrases):
            if index>max_wave_num:
                exit()
            step_index = pi % len(steps)
            dim_index = int(pi / len(steps))
            dim = constant.AROUSALS[dim_index]
            if args.random_grade:
                grade = np.random.normal(.5, .3, 1)[0]
            else:
                grade = steps[step_index]
            index = shared.make_wav(voc, dim, grade, phrase, pi, index, path, play, out_file)
else:
    for vi, voc in enumerate(constant.VOICES):
        for pi, phrase in enumerate(phrases):
            for dim in constant.AROUSALS:
                for grade in steps:
                    if index>max_wave_num:
                        exit()
                    if args.random_grade:
                        grade = np.random.normal(.5, .3, 1)[0]
                    index = shared.make_wav(voc, dim, grade, phrase, pi, index, path, play, out_file)