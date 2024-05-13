@echo off
echo Starting the application....

setx LOG_LEVEL "INFO"
setx CAMERA_INDEX 0
setx CACHE_EXPIRATION_IN_SECONDS 60
setx VOICE_EXPIRY_SECONDS 90
echo Setting envionment variables...

pip install --upgrade setuptools
py -m ensurepip --upgrade
py -m pip install --upgrade pip

echo Installing basic pip libraries....

start cmd /k "python main.py"
echo Starting Face Identifier....

start cmd /k "python file-transfer.py"
echo Starting Database Transfer....

start cmd /k "nodemon gui/server.js"
echo Starting the server....

echo Opening Google Chrome...
start "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" http://localhost:1100
echo Link VnoU-Identifier opened in Google Chrome

pause
