import smtplib, ssl
import logging

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class EmailSender:
    port = None
    smtp_server = None
    sender_email = None
    password = None
    email_enabled = None

    def __init__(
        self,
        smtp_server: str,
        sender_email: str,
        password: str,
        receiver: str,
    ):
        self.port = 465  # For SSL
        self.smtp_server = smtp_server
        self.sender_email = sender_email
        self.password = password
        self.receiver = receiver

    def email_pnl(self, pnl: float):
        subject = "Updated PNL"
        body = f"We got a new pnl ... i hope it is positive ${round(pnl,4)}"
        self._send_email(subject=subject, body=body)

    def email_error_msg(self, msg):
        subject = "There's been an error"
        body = msg
        self._send_email(subject=subject, body=body)

    def email_new_order(self, message: str, entry_filename, strategy_filename):
        subject = "Order has been placed"
        body = message
        self._send_email(subject=subject, body=body, entry_filename=entry_filename, strategy_filename=strategy_filename)

    def _send_email(self, subject, body, entry_filename=None, strategy_filename=None):
        em = MIMEMultipart()
        em["From"] = self.sender_email
        em["To"] = self.receiver
        em["Subject"] = subject
        em.attach(MIMEText(body))
        self._attach_image(em=em, entry_filename=entry_filename, strategy_filename=strategy_filename)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=self.smtp_server, port=self.port, context=context) as server:
            server.login(user=self.sender_email, password=self.password)
            server.sendmail(from_addr=self.sender_email, to_addrs=self.receiver, msg=em.as_string())

    def _attach_image(self, em, entry_filename, strategy_filename):
        if entry_filename is not None:
            with open(file=entry_filename, mode="rb") as f:
                img_data = f.read()
                em.attach(MIMEImage(img_data, name=entry_filename))
            f.close()
        if strategy_filename is not None:
            with open(file=strategy_filename, mode="rb") as f:
                img_data = f.read()
                em.attach(MIMEImage(img_data, name=strategy_filename))
            f.close()
