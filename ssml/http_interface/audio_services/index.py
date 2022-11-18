from typing import Text
import numpy as np
from flask import Flask, jsonify, request, make_response, send_file
import io
from emoreco import Emoreco
from textreco import Textreco
from textsynth import Textsynth
from emofusion import EmoFusion

import json
import soundfile as sf
import os
from io import BytesIO

app = Flask(__name__)

emoreco = Emoreco()
textreco = Textreco()
textsynth = Textsynth()
emofusion = EmoFusion()

@app.route('/audio_emo', methods=['POST'])
def add_audio_emo():
  audio_content = request.files['audio'].read()
  sig, fs = sf.read(io.BytesIO(audio_content))
  print(f'sampling rate: {fs}, signal shape: {sig.shape}')

  json_data = json.load(request.files['data'])  

  # os.system('play ./tmp.wav')
  prediction = emoreco.predict(sig)
  res_dict = {"a": np.float64(prediction[0]),
              "d": np.float64(prediction[1]),
              "p": np.float64(prediction[2])}
  json_data['emotion-audio'] = res_dict
  response = make_response(jsonify(json_data), 200)
  response.mimetype = 'application/json'
  return response

@app.route('/audio_asr', methods=['POST'])
def add_audio_asr():
  audio_content = request.files['audio'].read()
  sig, fs = sf.read(io.BytesIO(audio_content))
  print(f'sampling rate: {fs}, signal shape: {sig.shape}')

  json_data = json.load(request.files['data'])  
  lang = json_data['lang']

  # os.system('play ./tmp.wav')
  prediction = textreco.predict(sig, lang)
  json_data['text'] = prediction
  response = make_response(json_data, 200)
  response.mimetype = 'application/json'
  return response

@app.route('/audio_tts', methods=['POST'])
def add_audio_tts():
  json_data = request.json
  method = json_data['ssml_method']
  
  text = json_data['text']
  lang = json_data['lang']
  print(f'synthesizing: {text}')

  emo_dict = json_data['emotion-audio']

  audiosamples = BytesIO(textsynth.synth(
    text,
    lang=json_data['lang'],
    gender=json_data['gender'],
    pleasure=emo_dict['p'],
    arousal=emo_dict['a'],
    dominance=emo_dict['d'],
    method=method,
  ))
  
  response = make_response(audiosamples.getvalue())
  response.headers['Content-Type'] = 'audio/wav'
  response.headers['Content-Disposition'] = 'attachment; filename=sound.wav'

  return response



@app.route('/emo_fusion', methods=['POST'])
def add_emo_fusion():
  json_data = json.load(request.files['data'])
  prediction = emofusion.predict(json_data)
  for dim in ["a", "p", "d"]:
    prediction[dim] = np.float64(prediction[dim])
  json_data["emotion-fusion"] = prediction
  response = make_response(jsonify(json_data), 200)
  response.mimetype = 'application/json'
  return response

