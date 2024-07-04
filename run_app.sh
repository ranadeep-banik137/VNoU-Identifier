#!/bin/bash

export LOG_LEVEL="INFO"
export CAMERA_INDEX=0
export RETRY_INDEX=5
export CACHE_EXPIRATION=60

pip install --upgrade setuptools
py -m ensurepip --upgrade
py -m pip install --upgrade pip

pip install virtualenv
virtualenv face_recognition_env
#face_recognition_env\scripts\activate (Windows)
source face_recognition_env/bin/activate

# Install below package for ubuntu
sudo apt update
sudo apt install libgl1-mesa-glx


nohup python3 main.py &
