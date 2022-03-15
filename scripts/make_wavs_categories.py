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

args = parser.parse_args()

with open(args.texts) as f:
    phrases = f.readlines()

out_file = args.of
play = args.play
wav_folder = args.wavs

phrases = [p.split('\t')[-1].strip() for p in phrases]

# maximum number of generate wav files
max_wave_num = 40
min_length = 500
index = 0
path = audeer.mkdir(wav_folder)+'/'

with open(out_file, 'a') as of:
    of.write('file,emotion,speaker,gender\n')

# our set of categorical emotions
emotions = constant.EMOTIONS
voices = constant.VOICES
phrase_index = 0
while index<max_wave_num:
    if args.change_phrase:
        # if we want a new phrase for each sentence 
        for vi, voc in enumerate(voices):
            phrase = phrases[phrase_index]
            emo_index = phrase_index % len(emotions) - 1
            emo = emotions[emo_index]
            index = shared.make_wav_cat(voc, emo, phrase, phrase_index, index, path, play, out_file)
    else:
        # else we use the same phrase for all voices and all emotion categories
        phrase = phrases[phrase_index]
        for vi, voc in enumerate(voices):
            for ei, emo in enumerate(emotions):
                index = shared.make_wav_cat(voc, emo, phrase, phrase_index, index, path, play, out_file)
        phrase_index += 1
