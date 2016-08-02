# coding=utf-8
import json
import logging
import base64
import os
import re

from google.appengine.api import urlfetch
from google.appengine.api.app_identity import app_identity

SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
SENDGRID_SENDER = os.environ['SENDGRID_SENDER']

global_body = "pdf sucks!"


def send_email_back(recipient, subject, attachments, text_content=None, html_content=None):
    from sendgrid.helpers import mail
    from sendgrid.helpers.mail import Attachment
    import premailer

    logging.info("sending mail to %s (%s/%s)", recipient, SENDGRID_API_KEY, SENDGRID_SENDER)

    to_email = mail.Email(recipient)
    from_email = mail.Email(SENDGRID_SENDER)

    message = mail.Mail()

    message.set_from(from_email)
    message.set_subject(subject)

    personalization = mail.Personalization()
    personalization.add_to(to_email)
    message.add_personalization(personalization)

    if not text_content and not html_content:
        message.add_content(mail.Content("text/plain", global_body))

    if text_content:
        message.add_content(mail.Content("text/plain", text_content))

    if html_content:
        message.add_content(mail.Content("text/html", html_content))

    for att in attachments:
        data = att["data"]
        file_name = att["name"]

        if file_name.endswith(".htm") or file_name.endswith(".html"):
            stub_css = "https://%s.appspot.com/css/stub.css" % app_identity.get_application_id()
            data = re.sub(
                r'\"D:\\ssis\\SecureMail\\SecureMailTest\\MailItemImages\\BankB1\.gifstyle\.css&#xA;.*\"',
                '"%s"' % stub_css,
                data)

            logging.info("before transform(%s) %s", type(data), data)

            logging.info("using premailer for %s", file_name)

            data = data.decode("utf8")

            p = premailer.Premailer(data)
            data = p.transform().encode("utf8")

            logging.info("after transform(%s) %s", type(data), data)

        attachment = Attachment()
        attachment.set_content(base64.b64encode(data))
        attachment.set_type(att["type"])
        attachment.set_filename(att["name"])
        attachment.set_disposition("attachment")
        attachment.set_content_id(att["name"])
        message.add_attachment(attachment)

    data = json.dumps(message.get())

    logging.debug("sending %s", data)

    headers = {
        "Authorization": 'Bearer {0}'.format(SENDGRID_API_KEY),
        "Content-Type": "application/json",
        "Accept": 'application/json'
    }

    response = urlfetch.fetch(
        url="https://api.sendgrid.com/v3/mail/send",
        payload=data,
        method=urlfetch.POST,
        headers=headers)

    if response.status_code > 299:
        logging.error("response %s(%s)", response.content, response.status_code)
    else:
        logging.info("response %s(%s)", response.content, response.status_code)

    if response.status_code > 299:
        raise Exception("Failed to call sendgrid API")



