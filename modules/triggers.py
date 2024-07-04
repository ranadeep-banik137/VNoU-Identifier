import logging
import time
import datetime
from modules.database import fetch_table_data_in_tuples
from constants.db_constansts import query_data
from modules.mail_generators import send_mail, is_email_id_valid
from modules.config_reader import read_config
from modules.data_reader import fetch_first_element_in_tuple
from modules.app_logger import log_notification
from modules.data_cache import cache_email_reporting_items

config = read_config()


def trigger_mail(_id, name, images=[]):
    # _id = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name))
    receiver_email = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.EMAIL_FOR_ID % _id))  # 'ranadeep_banik@yahoo.com' for test purpose
    cc_email = ''
    bcc_email = ''
    if _id <= 0:
        pass
    # if not is_user_already_identified(name):
    img_text = """NB: Please provide confirmation if the image attached to the mail is yours.
    REPLY with 'yes, its me' or 'No, that is someone else'
    we would await your kind response."""
    subject = 'User detection email' if len(images) > 0 else '[No Reply] User detection mail'
    body = f"""Hi {name},
    
Hope you’re in the pink of health. This message is to enquire about your presence noticed at VNoU Solutions.
    
Our system has identified you visiting at our VNoU location at {datetime.datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format'])}.
In case of any further help needed please contact below:
                
- helpline number : 00011123498.
- Website : https://www.vnou-solutions.com/assist
                
We wish you have a pleasant day.
                
{img_text if len(images) > 0 else ''}
                
Regards,
VNoU Team"""

    if is_email_id_valid(receiver_email):
        logging.info(f'Sending mail to {receiver_email} attaching {len(images)} image/images')
    mail_sent, mail_time = send_mail(receiver_email=receiver_email, cc_email=cc_email, bcc_email=bcc_email, subject=subject, body=body, images=images)
    cache_email_reporting_items(_id=_id, name=name, email_id=receiver_email, is_email_sent=mail_sent, email_sent_at=mail_time, img_data=images)
    if mail_sent:
        log_notification(user_id=_id, name=name, images=images, email=receiver_email, email_sent=mail_sent, cc_email=cc_email, bcc_email=bcc_email, subject=subject, mail_sent_at=mail_time)
        logging.debug(f'mail sent with body {body}')
