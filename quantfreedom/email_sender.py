import smtplib, ssl
import os
import logging

from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

gmail_pw = os.getenv("gmail_password")
gmail_sender = os.getenv("gmail_sender")


class EmailSender:
    port = None
    smtp_server = None
    sender_email = None
    password = None
    email_enabled = None

    def __init__(self, config=None):
        self.port = 465  # For SSL
        self.smtp_server = "smtp.gmail.com"
        self.sender_email = "cryptofreedom1022@gmail.com"  # gmail_sender  # Enter your address
        self.password = "ripwldtyyjghlvfv"  # gmail_pw

        self.email_enabled = config.is_email_enabled() if config is not None else False

    def email_verification(self, user_name, user_email, rand_num):
        receiver_email = user_email  # Enter receiver address
        subject = f"Verify your CryptoFreedom1022 Copy Trading Account"
        body = MIMEText(
            f"""Dear {user_name}
            Your verification code:
        {rand_num}
            The verification code will be valid for 5 minutes.
            Please do not share this code with anyone.
            Don’t recognize this activity? Please reset your password and contact customer support immediately.
            This is an automated message, please do not reply.
            """
        )

        self._send_email(receiver_email, subject, body)

    def email_error_msg(self, msg, email_dst="jx128jx@gmail.com"):
        subject = "There's been an error"
        body = msg
        self._send_email(email_dst, subject, body)

    def email_new_order(self, fig_filename, email_dst="jx128jx@gmail.com"):
        subject = "Order has been placed"
        body = "A new order has been placed successfully"
        self._send_email(email_dst, subject, body, fig_filename)

    def email_server_has_stoped(self, email_dst="jx128jx@gmail.com"):
        subject = "Server has stoped"
        body = "Server is no longer running"
        self._send_email(email_dst, subject, body)

    def _send_email(self, receiver_email, subject, body, fig_filename=None):
        if self.email_enabled:
            logging.info(f"Notifying by email to [{receiver_email}]")
            em = MIMEMultipart()
            em["From"] = self.sender_email
            em["To"] = receiver_email
            em["Subject"] = subject
            em.attach(MIMEText(body))
            self._attach_image(em, fig_filename)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, receiver_email, em.as_string())
        else:
            logging.info("Email disabled, not sending email")

    def _attach_image(self, msg, fig_filename):
        if fig_filename is not None:
            with open(fig_filename, "rb") as f:
                img_data = f.read()
                msg.attach(MIMEImage(img_data, name=fig_filename))


if __name__ == "__main__":
    sender = EmailSender()
    sender.email_new_order("images\\08-21-2023_10-55-05.png", "gonzalo.a.r@gmail.com")
