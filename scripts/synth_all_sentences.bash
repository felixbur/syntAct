while IFS="," read -r col1 col2; do python scripts/say_emo.py --text "$col2" --emo neutral --voc de6 --wav $col1.wav --play ; done < texts/emodb_phrases.csv 
