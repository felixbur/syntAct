import  os
import audiofile as af
import audeer 
import argparse

errorFile = './synth_errors.txt'


parser = argparse.ArgumentParser(description='Script to generate synthesized wav files from text.')
parser.add_argument('--texts', help='The texts file', required=True)
parser.add_argument('--of', help='The output wave list', required=True)
parser.add_argument('--play', help='To play the wav files', action='store_true')

args = parser.parse_args()

with open(args.texts) as f:
    phrases = f.readlines()

out_file = args.of
play = args.play

phrases = [p.split('\t')[-1].strip() for p in phrases]

sexes = {'de1':'female', 'de2':'male', 'de3':'female', 'de4':'male', 'de6':'male', 'de7':'female'}

vocs = ['de1', 'de2', 'de3', 'de4', 'de6', 'de7']
#vocs = ['de6', 'de7']
emos = ['happy', 'angry', 'sad', 'neutral']
#emos = ['angry', 'neutral']
# maximum number of generate wav files
max_wave_num = 100
index = 0
path = audeer.mkdir('./wavs/')

for vi, voc in enumerate(vocs):
   for pi, phrase in enumerate(phrases):
        for ei, emo in enumerate(emos):
            if index>max_wave_num:
                exit()
            name = f'{voc}_{emo}_p{str(pi).zfill(6)}.wav'
            cmd = f'python ./scripts/sayEmo.py --emo {emo} --text \"{phrase}\" --voc {voc} --wav {path}/{name}'
            if play:
                cmd += ' --play'
            os.system(cmd)
            sig, sr = af.read(path+'/'+name)
            if len(sig) <= 100:
                try:
                    os.remove(name)
                except FileNotFoundError:
                    pass
                with open(errorFile, 'a') as ef:
                    ef.write('ERROR  on file %s\n' % name)
            else:
                index += 1
                with open(out_file, 'a') as of:
                    results = f'{path}/{name}, {emo}, {voc}, {sexes[voc]}\n'
                    of.write(results)
