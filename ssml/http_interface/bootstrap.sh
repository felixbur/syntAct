#!/bin/sh
export FLASK_APP=./audio_services/index.py
flask run -h 0.0.0.0
