import argparse
import json
import requests
import os


# terminal 1:
# bash ./bootstrap.sh
# terminal 2:
# source ~/.envs/easier_synt/bin/activate
# python send_request_tts.py -json ./json_code.json -mtd avd
#    (-mtd: avd|syntact|schroeder)

def tts(args):


    url_emo = "http://localhost:5000/audio_emo"
    url_asr = "http://localhost:5000/audio_asr"
    url_tts = "http://localhost:5000/audio_tts"
    outfile = args["output"]

    with open(args["json_code"], "r") as h:
        json_code = json.load(h)

    # pass SSML method via json 
    json_code["ssml_method"] = args["method"]
    
    print('testing TTS...')
    response = requests.post(url_tts, json=json_code)
    audio_bytes = response.content

    with open(outfile, "wb") as out:
        out.write(audio_bytes)
    print(f'Audio content written to file {outfile}')
    os.system(f'play {outfile}')

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="test tts wrapper")
    parser.add_argument('-json', '--json_code',
                        help='json file with emotion content',
                        type=str, required=False,
                        default="./json_code.json")
    parser.add_argument('-mtd', '--method',
                        help='SSML generation method: syntact, schroeder, avd',
                        type=str, required=False,
                        default="syntact")
    parser.add_argument('-o', '--output',
                        help='output audio file name',
                        type=str, required=False,
                        default="test_tts.wav")
    args = vars(parser.parse_args())
    tts(args)


    
