#!/bin/bash

export LOG_LEVEL="INFO"
export CAMERA_INDEX=0

pip install --upgrade setuptools
py -m ensurepip --upgrade
py -m pip install --upgrade pip

pip install virtualenv
virtualenv face_recognition_env
#face_recognition_env\scripts\activate (Windows)
source face_recognition_env/bin/activate
nohup python3 main.py &
