import os
import argparse
import sys
sys.path.append("./scripts")
import constant

# For windows: PhoPlayer.exe database="D:\Programme\mbrola\\"$3"\\"$3 tmp_e.pho /o=test.wav /t=wav;

parser = argparse.ArgumentParser(description='Call emofilt to generate wav file from text.')
parser.add_argument('--text', help='The text', required=True)
parser.add_argument('--emo1', help='The first emotion', required=True)
parser.add_argument('--grade1', help='The grade of the first emotion [0:1]', default='0.5')
parser.add_argument('--emo2', help='The second emotion', required=True)
parser.add_argument('--grade2', help='The grade of the second emotion [0:1]', default='0.5')
parser.add_argument('--voc', help='The voice', required=True)
parser.add_argument('--wav', help='The wav file', required=True)
parser.add_argument('--play', help='To play the wav file', action='store_true')

args = parser.parse_args()

voc = args.voc
text = args.text
emo1 = args.emo1
grade1 = float(args.grade1)
emo2 = args.emo2
grade2 = float(args.grade2)
wav_file = args.wav
pho_file = './tmp.pho'
play_file = args.play

# The weird thing is that MARY seems to diregard the voice sex, so the base F0 is always for men. 
# That's why we shift for females the mean F0 upwards
femalize = False
if voc == 'de1' or voc == 'de3':
	femalize = True
if femalize:
	cmd_make_pho = f'echo {text} | java -jar {constant.EMOFILT_PATH}emofilt.jar \
	-cf {constant.EMOFILT_CONFIG}emofiltConfig.ini -mary -voc {voc} -e femalize -of {pho_file}'
else:
	cmd_make_pho = f'echo {text} | java -jar {constant.EMOFILT_PATH}emofilt.jar \
	-cf {constant.EMOFILT_CONFIG}emofiltConfig.ini -mary -voc {voc} -e neutral -of {pho_file}'
os.system(cmd_make_pho)

# then we do the emotional simulation
cmd_emotionalize = f'java -jar {constant.EMOFILT_PATH}emofilt.jar \
-cf {constant.EMOFILT_CONFIG}emofiltConfig.ini -if {pho_file} -voc {voc} -e {emo1} -of {pho_file}'
# add the grade if necessary (grade/intensity goes from 0 for neutral to 1 for double effect, 
# with 0.5 being the "normal" grade)
if grade1 != 0.5:
	cmd_emotionalize += f' -gr {grade1}'
os.system(cmd_emotionalize)
# and once more for the second emotion
cmd_emotionalize = f'java -jar {constant.EMOFILT_PATH}emofilt.jar \
-cf {constant.EMOFILT_CONFIG}emofiltConfig.ini -if {pho_file} -voc {voc} -e {emo2} -of {pho_file}'
if grade2 != 0.5:
	cmd_emotionalize += f' -gr {grade2}'
os.system(cmd_emotionalize)

# lastly, we synthesize the pho file
cmd_mbrola = f'mbrola {constant.MBROLA_DB_PATH}{voc}/{voc} {pho_file} {wav_file}'	
print(cmd_mbrola)
os.system(cmd_mbrola)

if play_file:
	os.system(f'play {wav_file}')