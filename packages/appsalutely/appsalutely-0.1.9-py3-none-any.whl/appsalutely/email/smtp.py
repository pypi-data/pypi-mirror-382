from logging import getLogger
import smtplib
from email.message import EmailMessage
from .settings import ConnectionSettings

logger = getLogger(__name__)


class SMTP:
    def __init__(self, settings: ConnectionSettings):
        self.host = settings.host
        self.port = settings.port
        self.starttls = settings.starttls
        self.username = settings.username
        self.password = settings.password

        self.conn: smtplib.SMTP

    def __enter__(self):
        logger.debug("Connecting to SMTP server")
        conn_class = smtplib.SMTP if self.starttls else smtplib.SMTP_SSL
        self.conn = conn_class(self.host, self.port, timeout=30)
        if self.starttls:
            self.conn.starttls()
        logger.debug("Authenticating to SMTP server")
        self.conn.login(self.username, self.password.get_secret_value())
        logger.debug("Successfully connected to SMTP server")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("Disconnecting from SMTP server")
        try:
            self.conn.quit()
        except smtplib.SMTPException:
            logger.error("Failed to close connection", exc_info=True)

    def send_message(self, email: EmailMessage):
        logger.info(f"Sending email to {email['To']}")
        if email["To"] == self.username:
            logger.error("Cannot send email to self, discarding")
            return
        self.conn.send_message(email)
