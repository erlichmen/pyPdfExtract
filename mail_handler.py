# coding=utf-8
import logging
import re
import webapp2
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from emails import send_email_back

from deferred import do_defer
from pdf_utils import extract_embedded


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: %s => %s", mail_message.sender, mail_message.to)

        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        decoded_text = None

        for content_type, body in plaintext_bodies:
            decoded_text = body.decode()

            logging.debug("decoded_text(%s): %s", content_type, decoded_text)

            p = re.compile(ur'(https:\/\/mail\.google\.com\/mail\/.*)')
            m = re.search(p, decoded_text)

            if m is None:
                continue

            url = m.group(0)

            logging.info("going to validate url at %s", url)

            urlfetch.fetch(url)

        decoded_html = None

        for content_type, body in html_bodies:
            decoded_html = body.decode()
            logging.debug("decoded_html(%s): %s", content_type, decoded_html)

        if hasattr(mail_message, 'attachments'):
            password = str(mail_message.to).split("@")[0].split("+")[1]
            attachments = []

            for fn, att in mail_message.attachments:
                logging.info("Attachment filename is %s", fn)

                for filename, data in extract_embedded(att.decode(), password):
                    logging.info("found attachment %s size %s", filename, len(data))

                    attachments.append({
                        "data": data,
                        "name": filename,
                        "type": "application/pdf",
                    })

            text_content = decoded_text
            html_content = decoded_html

            do_defer(
                send_email_back,
                mail_message.sender, mail_message.subject, attachments,
                text_content=text_content, html_content=html_content, _tag="wheeee")


app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
