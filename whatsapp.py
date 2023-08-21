import json
import logging
import time

import pywhatkit
from twilio.rest import Client

TWILIO_ACCOUNT_SID = '<TWILIO_ACCOUNT_SID>'
TWILIO_AUTH_TOKEN = '<TWILIO_AUTH_TOKEN>'
CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

SANDBOX = '+14155238886'
PHONE_NUMBERS = {'+573XXXXXXXXX', '+57XXXXXXXXXX'}
INITIAL_MESSAGE = 'join kept-right'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def send_message(text):
    for phone in PHONE_NUMBERS:
        message = CLIENT.messages.create(
            body=text,
            from_=f'whatsapp:{SANDBOX}',
            to=f'whatsapp:{phone}'
        )
        logging.info(f"Se ha enviado el mensaje: {message.sid} a {message.to}")

def init_sandbox():
    pywhatkit.sendwhatmsg_instantly(SANDBOX, INITIAL_MESSAGE)
