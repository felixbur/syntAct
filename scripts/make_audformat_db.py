import os                       # file operations
import pandas as pd             # work with tables
pd.set_option('display.max_rows', 10)
import audata.define as define  # some definitions
import audata.utils as utils    # util functions
from audata import Database, AudioInfo, Rater, Scheme, Split, Column, Table
from audata.define import SplitType, RaterType

db = Database(
    name='synth_emofilt',
    source='intern',
    usage=define.Usage.COMMERCIAL,
    languages=[utils.str_to_language('de')],
    description='Synthesized audio files with emofilt in various emotions.')

db.media['tts'] = AudioInfo(sampling_rate=16000, channels=1, format='wav')
raters= {'gold'}

for rater in raters:
    db.raters[rater] = Rater(RaterType.HUMAN)

db.schemes['emotion'] = Scheme(
    labels=['neutral', 'happy', 'bored', 'angry'],
    description='Three basic emotions and neutral.')
lang = utils.str_to_language('de').name
map_speaker = {
    95: {'gender': define.Gender.MALE, 'language': lang, 'name': 'de1'},
    96: {'gender': define.Gender.FEMALE, 'language': lang, 'name': 'de2'},
    97: {'gender': define.Gender.MALE, 'language': lang, 'name': 'de3'},
    98: {'gender': define.Gender.FEMALE, 'language': lang, 'name': 'de4'},
    99: {'gender': define.Gender.MALE, 'language': lang, 'name': 'de6'},
    100: {'gender': define.Gender.FEMALE, 'language': lang, 'name': 'de7'},
}
db.schemes['speaker'] = Scheme(
        labels=map_speaker,
        description='Six mbrola voices for German')

pathroot = '/home/fburkhardt/ResearchProjects/emotion-synthesizer/scripts/'
filePath = pathroot + '/synthFiles.csv'
'''
path,emotion,speaker
wavs/000000_de1_happy_1.wav,happy,95
...
'''

df_csv = pd.read_csv(filePath, index_col=[0], converters={'file': lambda x: os.path.join('/home/fburkhardt/audb/synth-emofilt/audio', x)})
files=df_csv.index

db['emotion'] = Table(files=files)
db['emotion']['emotion'] = Column(
    scheme_id='emotion',
    rater_id='gold',
    has_confidence=False)
db['emotion']['emotion'].set(df_csv['emotion'])
db['emotion']['speaker'] = Column(scheme_id='speaker')
db['emotion']['speaker'].set(df_csv['speaker'])

path = os.path.expanduser('~/audb/synth_emofilt')
db.save(path)
print(db)