import smtplib
import ssl
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from modules.config_reader import read_config
from modules.data_reader import remove_file

config = read_config()


def connect_server():
    mail_config = config['mail']
    sender_email = mail_config['id']
    app_password = mail_config['password']  # Collect App Password from https://support.google.com/accounts/answer/185833?hl=en
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


def send_mail(receiver_email, cc_email='', subject='', body='', images=[]):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = config['mail']['id']
    message["To"] = receiver_email
    if cc_email != '':
        message["Cc"] = cc_email  # Add CC recipient
    message["Subject"] = 'Default Test Mail <VNoU-Solutions>' if subject.strip() == '' else subject
    message = set_message_for_mail(message, body, images)
    # Establish a secure session with the Yahoo Mail SMTP server
    try:
        server = connect_server()
        server.sendmail(config['mail']['id'], receiver_email, message.as_string())
        logging.info(f'mail sent to {receiver_email} successfully')
    except Exception as e:
        # Print any error messages to stdout
        logging.error(f'Error sending mail to {receiver_email} {e}')
    finally:
        server.quit()


def set_message_for_mail(message, body, image_files=[]):
    # Add body to email
    body = "This email contains images" if body.strip() == '' else body
    message.attach(MIMEText(body, "plain"))
    # image_files = ["../faces/Rana1.jpg"]
    delete_img_after_mail_post = config['mail']['delete-local-image']
    # Attach images to the email
    for image_file in image_files:
        try:
            with open(image_file, "rb") as attachment:
                part = MIMEImage(attachment.read(), name=os.path.basename(image_file))
                message.attach(part)
                # if delete_img_after_mail_post:
                    # remove_file(image_file)
                # TODO to delete the images after posting email
        except FileNotFoundError:
            print(f"Attachment file {image_file} not found")
    return message
