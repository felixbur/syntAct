import os
import argparse
import sys
sys.path.append("./scripts")
import constant

# For windows: PhoPlayer.exe database="D:\Programme\mbrola\\"$3"\\"$3 tmp_e.pho /o=test.wav /t=wav;

parser = argparse.ArgumentParser(description='Call emofilt to generate wav file from text.')
parser.add_argument('--text', help='The text', required=True)
parser.add_argument('--emo', help='The emotion', required=True)
parser.add_argument('--voc', help='The voice', required=True)
parser.add_argument('--wav', help='The wav file', required=True)
parser.add_argument('--grade', help='The grade of the emotions [-1:1]', default='.5')
parser.add_argument('--play', help='To play the wav file', action='store_true')

args = parser.parse_args()

voc = args.voc
text = args.text
emo = args.emo
wav_file = args.wav
pho_file = './tmp.pho'
play_file = args.play
grade = float(args.grade)

# The weird thing is that MARY seems to diregard the voice sex (for de1 and de3), 
# so the base F0 is always for men. 
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
-cf {constant.EMOFILT_CONFIG}emofiltConfig.ini -if {pho_file} -voc {voc} -e {emo} -of {pho_file}'
# add the grade if necessary (grade/intensity goes from 0 for neutral to 1 for double effect, 
# with 0.5 being the "normal" grade)
if grade != .5:
	cmd_emotionalize += f' -gr {grade}'

os.system(cmd_emotionalize)

# lastly, we synthesize the pho file
cmd_mbrola = f'mbrola {constant.MBROLA_DB_PATH}{voc}/{voc} {pho_file} {wav_file}'	
print(cmd_mbrola)
os.system(cmd_mbrola)

if play_file:
	os.system(f'play {wav_file}')