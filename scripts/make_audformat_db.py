import os                       # file operations
import pandas as pd             # work with tables
pd.set_option('display.max_rows', 10)
import audformat.define as define  # some definitions
import audformat.utils as utils    # util functions
from audformat import Database, Rater, Scheme, Table, Media, Column
from audformat.define import RaterType
import sys
sys.path.append("./scripts")
import constant

db_name = 'syntact'
in_file = 'list.csv'

db = Database(
    name=db_name,
    source='intern',
    usage=define.Usage.UNRESTRICTED,
    languages=[utils.map_language('de')],
    description='Synthesized audio files with emofilt in various emotions.')

db.media['tts'] = Media(sampling_rate=16000, channels=1, format='wav')
raters= {'gold'}

for rater in raters:
    db.raters[rater] = Rater(RaterType.HUMAN)

db.schemes['emotion'] = Scheme(
    labels=constant.EMOTIONS,
    description='Three basic emotions and neutral.')
lang = utils.map_language('de')
map_speaker = {
    'de1': {'gender': define.Gender.MALE, 'language': lang},
    'de2': {'gender': define.Gender.FEMALE, 'language': lang},
    'de3': {'gender': define.Gender.MALE, 'language': lang},
    'de4': {'gender': define.Gender.FEMALE, 'language': lang},
    'de6': {'gender': define.Gender.MALE, 'language': lang},
    'de7': {'gender': define.Gender.FEMALE, 'language': lang},
}
db.schemes['speaker'] = Scheme(
        labels=map_speaker,
        description='Six mbrola voices for German')

pathroot = './'
filePath = pathroot + in_file
'''
path,emotion,speaker
wavs/000000_de1_happy_1.wav,happy,de1
...
'''

#df_csv = pd.read_csv(filePath, index_col=[0], converters={'file': lambda x: os.path.join('/home/fburkhardt/audb/synth-emofilt/audio', x)})
df_csv = pd.read_csv(filePath, index_col=[0], header=0)

db['files'] = Table(index=df_csv.index)
db['files']['emotion'] = Column(
    scheme_id='emotion',
    rater_id='gold')
db['files']['emotion'].set(df_csv['emotion'])
db['files']['speaker'] = Column(scheme_id='speaker')
db['files']['speaker'].set(df_csv['speaker'])

path = f'./{db_name}'
db.save(path)
print(db)