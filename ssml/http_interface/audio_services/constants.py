"""
Python constants to simulate emotional arousal based on SSML modifications

@author Felix Burkhardt
@copyright audEERING GmbH

"""

MIN_VOLUME, MID_VOLUME, MAX_VOLUME =  -10, 0, 20
MIN_PITCH, MID_PITCH, MAX_PITCH = -50, 0, 80
MIN_RATE, MID_RATE, MAX_RATE = 50, 100, 200
NEUTRAL_PITCH, NEUTRAL_RATE, NEUTRAL_VOLUME = 0, 100, 0
  
METHOD_SCHROEDER = 'schroeder'
METHOD_SYNTACT = 'syntact'
METHOD_AVD = 'avd'
METHOD_PASS = 'none'

GENDER_NEUTRAL = 'NEUTRAL'
GENDER_MALE = 'MALE'
GENDER_FEMALE = 'FEMALE'
