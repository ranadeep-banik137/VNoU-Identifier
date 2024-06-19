import os
import re
import datetime
import time
import logging
import pyttsx3
from gtts import gTTS
from playsound import playsound
from googletrans import Translator
from modules.database import fetch_table_data_in_tuples, populate_identification_record
from constants.db_constansts import query_data
from modules.config_reader import read_config
from pydub import AudioSegment
from pydub.playback import play
from modules.db_miscellaneous import is_user_already_identified

config = read_config()


def play_speech(input_name=''):
    # It is a text value that we want to convert to audio
    if input_name == 'None' or input_name is None or input_name == '':
        pass
    else:
        text_val = f'Sorry, I cannot identify your face currently. Please stand in front of the camera for a while' if input_name == 'Unknown Face' else f'Welcome {input_name}. I cannot interact with you but good to see you here. Have a nice day {input_name}'
        # Here are converting in English Language
        language = 'en'
        speech_file_name = input_name.split(' ')[0] + '_' + re.sub("[^\w]", "_",
                                                                   datetime.datetime.fromtimestamp(
                                                                       time.time()).strftime(
                                                                       config['app_default']['timestamp-format']))
        # Passing the text and language to the engine,
        # here we have assign slow=False. Which denotes
        # the module that the transformed audio should
        # have a high speed
        # obj = gTTS(text=text_val, lang=language, slow=False)

        if not is_user_already_identified(input_name):
            logging.info(f'Playing audio for {input_name}' if input_name != "Unknown Face" else '')

            # Here we are saving the transformed audio in a mp3 file
            # obj.save(f"{os.getenv('PROJECT_PATH') or ''}data/{speech_file_name}.mp3")
            # logging.debug(f'file saved as {speech_file_name}.mp3')
            try:
                play_speech_without_saving_audio(text_val)
                # Play the exam.mp3 file
                # playsound(f"{os.getenv('PROJECT_PATH') or ''}data/{speech_file_name}.mp3")
                # audio = AudioSegment.from_file(f"{os.getenv('PROJECT_PATH') or ''}data/{speech_file_name}.mp3")
                # play(audio)
                logging.debug(f'Playing : {text_val}')
            except Exception as err:
                logging.error(err)
            finally:
                # os.remove(f'{os.getenv("PROJECT_PATH") or ""}data/{speech_file_name}.mp3')
                # logging.debug(f'Removed {speech_file_name}.mp3')
                return True if input_name != 'Unknown Face' else False


def play_speech_without_saving_audio(text=''):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech (words per minute)
    engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
    # translator = Translator()
    # translated = translator.translate(text, dest='bn')
    # beng = translated.text
    # print(beng)
    engine.say(text)
    engine.runAndWait()
