import smtplib
import ssl
import os
import logging
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from modules.config_reader import read_config
from modules.data_reader import remove_file, save_encoded_image_data

config = read_config()


def connect_server():
    mail_config = config['mail']
    sender_email = mail_config['id']
    app_password = mail_config['password']  # Collect App Password from https://myaccount.google.com/apppasswords
    smtp_server = mail_config['host']
    port = int(mail_config['port'])  # For starttls
    server = None
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, app_password)
    except Exception as error:
        logging.error(f'Error encountered while sending mail {error}')
    return server


def send_mail(receiver_email, cc_email='', bcc_email='', subject='', body='', images=[]):
    mail_sent_at = None
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = config['mail']['id']
    message["To"] = receiver_email
    if cc_email != '':
        message["Cc"] = cc_email  # Add CC recipient
    message["Subject"] = 'Default Test Mail <VNoU-Solutions>' if subject.strip() == '' else subject
    message = set_message_for_mail_with_binary_images(message, body, images)
    # Establish a secure session with the SMTP server
    try:
        server = connect_server()
        server.sendmail(config['mail']['id'], receiver_email, message.as_string())
        logging.info(f'mail sent to {receiver_email} successfully')
        mail_sent_at = datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format'])
        mail_sent = True
    except smtplib.SMTPException as e:
        mail_sent = False
        logging.info('Daily sending limit exceeded. Please wait 24 hours before trying again.' if 'Daily user sending limit exceeded' in str(e) else f'Error sending mail to {receiver_email} {e}')
    except Exception as e:
        mail_sent = False
        logging.error(f'Error sending mail to {receiver_email} {e}')
    finally:
        server.quit()
        if not mail_sent and str(config['mail']['save-image-to-local']) == 'True':
            for image_data, image_name in images:
                save_encoded_image_data(image_data, f'{config["files"]["save-unknown-image-filepath"]}{image_name}')
                logging.info(f'Pictures saved to local as sending mail to {receiver_email} has failed')
        return mail_sent, mail_sent_at


def set_message_for_mail_with_image_files(message, body, image_files=[]):
    # Add body to email
    body = "This email contains images" if body.strip() == '' else body
    message.attach(MIMEText(body, "plain"))

    # Attach images to the email
    for image_file in image_files:
        try:
            with open(image_file, "rb") as attachment:
                part = MIMEImage(attachment.read(), name=os.path.basename(image_file))
                message.attach(part)
        except FileNotFoundError:
            print(f"Attachment file {image_file} not found")
    return message


def set_message_for_mail_with_binary_images(message, body, image_data_list=[]):
    # Add body to email
    body = "This email contains images" if body.strip() == '' else body
    message.attach(MIMEText(body, "plain"))

    # Attach images to the email
    for image_data, image_name in image_data_list:
        part = MIMEImage(image_data, name=image_name)
        message.attach(part)
    return message
