import os                       # file operations
import pandas as pd             # work with tables
import audformat.define as define  # some definitions
import audformat.utils as utils    # util functions
from audformat import Database, Rater, Scheme, Table, Media, Column, Split
from audformat.define import RaterType, DataType, SplitType
import sys
sys.path.append("./scripts")
import constant

db_name = 'syntact_dim'
in_file = 'synth_out.csv'

db = Database(
    name=db_name,
    source='intern',
    usage=define.Usage.UNRESTRICTED,
    languages=[utils.map_language('de')],
    description='Synthesized audio files with emofilt in various grades of arousal and valence.')

db.media['tts'] = Media(sampling_rate=16000, channels=1, format='wav')
raters= {'gold'}

for rater in raters:
    db.raters[rater] = Rater(RaterType.HUMAN)

db.schemes['arousal'] = Scheme(
    DataType.FLOAT,
    minimum=0,
    maximum=1,
    description='A value for arousal')

db.schemes['valence'] = Scheme(
    DataType.FLOAT,
    minimum=0,
    maximum=1,
    description='A value for valence')

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
file,speaker,gender,arousal,valence
/data/fburkhardt/syntAct/synthesized_audio/de1_p000000_0.301_0.576.wav,de1,female,0.301,0.576
...
'''

#df_csv = pd.read_csv(filePath, index_col=[0], converters={'file': lambda x: os.path.join('/home/fburkhardt/audb/synth-emofilt/audio', x)})
df_csv = pd.read_csv(filePath, index_col=[0], header=0)


# re-scale the values from 0-1
def rescale(input, min, max, newmin, newmax):
    oldrange = max-min
    newrange = newmax - newmin
    return (((input - min) * newrange) / oldrange) + newmin

for dimension in ['arousal', 'valence']:
    min = df_csv[dimension].min()
    max = df_csv[dimension].max()
    df_csv[dimension] = df_csv[dimension].map(lambda x: rescale(x, min, max, 0, 1))

# create a files table
db['files'] = Table(index=df_csv.index)
db['files']['speaker'] = Column(scheme_id='speaker')
db['files']['speaker'].set(df_csv['speaker'])


# a dictionary to assign speakers to splits
split2speakers = {
    SplitType.TRAIN: ['de1', 'de2', 'de3', 'de4'],
    SplitType.TEST: ['de6', 'de7']
}

# a rater type
db.raters['desired'] = Rater(type=RaterType.OTHER)

# for both splits
for split, speakers in split2speakers.items():
    db.splits[split] = Split(type=split)
    split_category_df = df_csv[df_csv['speaker'].isin(speakers)]
    db[f'emotion.dimensions.{split}.desired'] = Table(index=split_category_df.index, split_id=split)
    # for both dimensions
    for dimension in ['arousal', 'valence']:
        db[f'emotion.dimensions.{split}.desired'][dimension] = Column(scheme_id=dimension, rater_id='desired')
        db[f'emotion.dimensions.{split}.desired'][dimension].set(split_category_df[dimension])


path = f'./{db_name}'
db.save(path)
print(db)