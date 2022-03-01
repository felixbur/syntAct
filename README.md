# syntAct
Scripts to generate a database of simulated emotional expression.

These scripts might help to synthesize a database of simulated emotional expression.

You need in addition:

* a text corpus 
* the [emofilt software](http://emofilt.syntheticspeech.de/)
* the [MARY tts software version 4.3.1](http://mary.dfki.de/download/index.html#mary-tts-4x) (version 5 is without Mbrola support)
* the [MBROLA software](https://github.com/numediart/MBROLA)

## Contents
### scripts
Scripts to generate the database and convert to audformat in Python.

## Installation

* install emofilt (to emotionalize the output)
* install MARY 4.x (for German NLP)
* install mbrola (for diphone DSP)
* install the German voices de1, de2, de3, de4, de6, de7
* (install other voices if you have a NLP for the language)
* install python version >= 3.6
* install and activate a python virtual environment
* adjust paths in scripts/constant.py

## Usage

* This has been tried ONLY on Ubuntu 20 (but should run with any linux)
* try as first test the script say_emo.py:
```
python scripts/sayEmo.py --text "das Boot ist voll aber es können noch Leute rein" --emo sad --voc de6 --wav test.wav --play
```

* Next, you might try to generate a whole set of wave files:
```
python scripts/make_wavs.py --texts demo/texts.txt --of list.cs
```
* Finally, you might try to make an [audformat](https://audeering.github.io/audformat/index.html) database with
```
python scripts/make_audformat_db.py
```

* If you like, you can try your new database with [nkululeko](https://github.com/felixbur/nkululeko/)
* Here's a suggestions for an .ini file:
```
[EXP]
root = ./tests/
name = exp_syntact
runs = 1
epochs = 1
save = True
[DATA]
databases = ['syntact']
syntact = /home/felix/data/research/syntAct/syntact/
syntact.split_strategy = speaker_split
syntact.testsplit = 50
syntact.value_counts = True
target = emotion
labels = ['angry', 'happy', 'neutral', 'sad']
[FEATS]
#type = trill
type = os
scale = standard
[MODEL]
type = svm
save = True
[PLOT]
value_counts = True
tsne = True
```