import logging
import time
import datetime
from modules.database import fetch_table_data_in_tuples
from constants.db_constansts import query_data
from modules.mail_generators import send_mail
from modules.config_reader import read_config
from modules.db_miscellaneous import is_user_already_identified
from modules.data_reader import fetch_first_element_in_tuple

config = read_config()


def trigger_mail(name, images=[]):
    _id = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name))
    identified_at = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.TIME_IDENTIFIED_FOR_ID % _id))
    receiver_email = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.EMAIL_FOR_ID % _id))  # 'ranadeep_banik@yahoo.com' for test purpose
    if 'example.com' not in receiver_email and receiver_email != '' and receiver_email is not None:
        cc_email = ''
        if _id <= 0:
            pass
        if not is_user_already_identified(name):
            img_text = """NB: Please provide confirmation if the image attached to the mail is yours.
            REPLY with 'yes, its me' or 'No, that is someone else'
            we would await your kind response."""
            subject = 'User detection email' if len(images) > 0 else '[No Reply] User detection mail'
            body = f"""Hi {name},
    
    Hope you’re in the pink of health. This message is to enquire about your presence noticed at VNoU Solutions.
    
    Our system has identified you visiting at our VNoU location at {identified_at if identified_at is not None else datetime.datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format'])}.
    In case of any further help needed please contact below:
                
    - helpline number : 00011123498.
    - Website : https://www.vnou-solutions.com/assist
                
    We wish you have a pleasant day.
                
    {img_text if len(images) > 0 else ''}
                
    Regards,
    VNoU Team"""

            send_mail(receiver_email=receiver_email, cc_email=cc_email, subject=subject, body=body, images=images)
            logging.info(f'Sending mail to {receiver_email} with body {body} along with {len(images)} images')
            logging.debug(f'mail sent with body {body}')
    else:
        logging.warning(f'Either mail id not found or domain not valid for user {name}. Skipping mail tigger')
