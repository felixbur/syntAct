# syntAct
Scripts to generate a database of simulated emotional expression.

These scripts might help to synthesize a database of simulated emotional expression.

You need in addition:

* a text corpus 
* the emofilt software
* the MARY tts software (or another one that generates phonetic descriptions from text)
* the MBROLA software

## Contents

### emofilt_config
The emofilt parameters are stored here.
Most importantly, you defince the possible emotion categories in emotions.xml

### scripts
Scripts to generate the database and convert to audformat in Python.