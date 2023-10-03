import smtplib, ssl
import logging

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from my_stuff import EmailAccount


class EmailSender:
    port = None
    smtp_server = None
    sender_email = None
    password = None
    email_enabled = None

    def __init__(self):
        self.port = 465  # For SSL
        self.smtp_server = EmailAccount.smtp_server
        self.sender_email = EmailAccount.sender_account
        self.password = EmailAccount.sender_password
        self.receiver = EmailAccount.receiver_account

    def email_error_msg(self, msg):
        subject = "There's been an error"
        body = msg
        self._send_email(subject=subject, body=body)

    def email_new_order(self, message: str, fig_filename):
        subject = "Order has been placed"
        body = message
        self._send_email(subject=subject, body=body, fig_filename=fig_filename)

    def _send_email(self, subject, body, fig_filename=None):
        logging.info(f"Notifying by email to [{self.receiver}]")
        em = MIMEMultipart()
        em["From"] = self.sender_email
        em["To"] = self.receiver
        em["Subject"] = subject
        em.attach(MIMEText(body))
        self._attach_image(em, fig_filename)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=self.smtp_server, port=self.port, context=context) as server:
            server.login(user=self.sender_email, password=self.password)
            server.sendmail(from_addr=self.sender_email, to_addrs=self.receiver, msg=em.as_string())

    def _attach_image(self, msg, fig_filename):
        if fig_filename is not None:
            with open(file=fig_filename, mode="rb") as f:
                img_data = f.read()
                msg.attach(MIMEImage(img_data, name=fig_filename))
