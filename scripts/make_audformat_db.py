import os                       # file operations
import pandas as pd             # work with tables
pd.set_option('display.max_rows', 10)
import audformat.define as define  # some definitions
import audformat.utils as utils    # util functions
from audformat import Database, Rater, Scheme, Table, Media, Column, Split
from audformat.define import RaterType, DataType, SplitType
import sys
sys.path.append("./scripts")
import constant

db_name = 'syntact_cat'
in_file = 'synth_out.csv'

db = Database(
    name=db_name,
    source='intern',
    usage=define.Usage.UNRESTRICTED,
    languages=[utils.map_language('de')],
    description='Synthesized audio files with emofilt in various emotions.')

db.media['tts'] = Media(sampling_rate=16000, channels=1, format='wav')

db.schemes['emotion'] = Scheme(
    #labels=constant.EMOTIONS,
    labels= ['anger', 'happiness', 'neutral', 'sadness', 'boredom', 'fear'],
    description='Five basic emotions and neutral.')

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

df_csv = pd.read_csv(filePath, index_col=[0], converters={'file': lambda x: './synthesized_audio/'+os.path.basename(x)})

# replace the labels
df_csv = df_csv.replace(['angry', 'happy', 'neutral', 'sad','bored', 'scared'], ['anger', 'happiness', 'neutral', 'sadness', 'boredom', 'fear'])

# a dictionary to assign speakers to splits
split2speakers = {
    SplitType.TRAIN: ['de1', 'de2', 'de3', 'de4'],
    SplitType.TEST: ['de6', 'de7']
}

# create a files table
db['files'] = Table(index=df_csv.index)
db['files']['speaker'] = Column(scheme_id='speaker')
db['files']['speaker'].set(df_csv['speaker'])

# a rater type
db.raters['desired'] = Rater(type=RaterType.OTHER)

# for both splits
for split, speakers in split2speakers.items():
    db.splits[split] = Split(type=split)
    split_category_df = df_csv[df_csv['speaker'].isin(speakers)]
    db[f'emotion.categories.{split}.desired'] = Table(index=split_category_df.index, split_id=split)
    db[f'emotion.categories.{split}.desired']['emotion'] = Column(scheme_id='emotion', rater_id='desired')
    db[f'emotion.categories.{split}.desired']['emotion'].set(split_category_df['emotion'])
        
path = f'./{db_name}'
db.save(path)
print(db)