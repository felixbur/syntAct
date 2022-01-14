import  os
import audiofile as af

phraseFile = '../news10K-sentences.txt'
outFile = 'synthPhraseOut.csv'
errorFile = 'synthPhraseErrors.csv'

with open(phraseFile) as f:
    phrases = f.readlines()

phrases = [p.split('\t')[-1].strip() for p in phrases]
# vocs = ['de1', 'de2', 'de3', 'de4', 'de6', 'de7']
vocs = ['de6', 'de7']
# emos = ['happy', 'angry', 'bored', 'neutral']
emos = ['angry', 'neutral']
phrasenum = 4000
speakerIds = {'de1':95, 'de2':96, 'de3':97, 'de4':98, 'de6':99, 'de7':100}
index = 0
path = '/home/fburkhardt/ResearchProjects/emotion-synthesizer/scripts/wavs/'
for (vi, voc) in enumerate(vocs):
   for (i, phrase) in enumerate(phrases[phrasenum*vi:(phrasenum*(vi+1))]):
        for emo in emos:
            text = str(1+phrasenum * vi + i)
            name = '%s%s_%s_%s_%s.wav' % (path, str(index).zfill(6), voc, emo, text)
#            print("%s" % (name))
            cmd = './sayEmo.sh '+emo+' \"'+phrase+'\" '+voc+' '+name+ '> /dev/null 2>> error.log'
            os.system(cmd)
            sig, sr = af.read(name)
            if len(sig) == 0:
                os.remove(name)
                with open(errorFile, 'a') as ef:
                    ef.write('ERROR  on file %s\n' % name)
            else:
                index += 1
                vocId = speakerIds.get(voc)
                with open(outFile, 'a') as of:
                    results = "%s,%s,%s\n" % (name, emo, vocId)
                    of.write(results)
