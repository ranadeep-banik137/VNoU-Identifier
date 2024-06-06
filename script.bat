@echo off
echo Starting the application....

setx LOG_LEVEL "INFO"
setx CAMERA_INDEX 0
setx FRAME_RATE_RANGE 5
setx FACE_RECOGNITION_MODEL "cnn"
setx CACHE_EXPIRATION_IN_SECONDS 10800
setx VOICE_EXPIRY_SECONDS 180
echo Setting envionment variables...

::pip install -r requirements.txt
pip install --upgrade setuptools
py -m ensurepip --upgrade
py -m pip install --upgrade pip

echo Installing basic pip libraries....

start /min cmd /k "python main.py"
echo Starting Face Identifier....

start /min cmd /k "python file-fetcher.py"
echo Starting Database Transfer....

start /min cmd /k "nodemon gui/server.js"
echo Starting the server....

echo Opening Google Chrome...
start "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" http://localhost:1100
echo Link VnoU-Identifier opened in Google Chrome

pause
