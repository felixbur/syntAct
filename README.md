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
* fit paths in scripts/constant.py

## Usage

* try as first test the script say_emo.py:
```
python scripts/sayEmo.py --text "das Boot ist voll aber es können noch Leute rein" --emo sad --voc de6 --wav test.wav
```