from .settings import ConnectionSettings
import imaplib
from email.message import EmailMessage
from email import policy, message_from_bytes
from logging import getLogger
from typing import Generator

logger = getLogger(__name__)


class IMAP:
    def __init__(self, settings: ConnectionSettings, folder: str = "INBOX"):
        self.host = settings.host
        self.port = settings.port
        self.starttls = settings.starttls
        self.username = settings.username
        self.password = settings.password
        self.folder = folder

        self.conn: imaplib.IMAP4
        self.last_uid: str | None = None

    def __enter__(self):
        logger.debug("Connecting to IMAP server")
        conn_class = imaplib.IMAP4 if self.starttls else imaplib.IMAP4_SSL
        self.conn = conn_class(self.host, self.port, timeout=30)
        if self.starttls:
            self.conn.starttls()
        logger.debug("Authenticating to IMAP server")
        self.conn.login(self.username, self.password.get_secret_value())
        logger.debug("Successfully connected to IMAP server")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("Disconnecting from IMAP server")
        try:
            self.conn.logout()
        except Exception:
            logger.error("Error disconnecting from IMAP server", exc_info=True)

    def poll(
        self,
    ) -> Generator[tuple[str, EmailMessage], None, None]:
        logger.debug(f"Polling IMAP folder {self.folder}")
        self.conn.select(self.folder)
        if self.last_uid is not None:
            last_uid = self.last_uid
            result, uiddata = self.conn.uid("search", None, f"UID {self.last_uid}:*")  # type: ignore
        else:
            last_uid = "\0"
            result, uiddata = self.conn.uid("search", None, "ALL")  # type: ignore
        if result != "OK":
            raise RuntimeError(
                f"Failed to search for emails in folder {self.folder}: {result}"
            )
        uids: list[bytes] = uiddata[0].split()
        for uidb in uids:
            uid = uidb.decode("utf-8")
            if uid <= last_uid:
                continue
            result, data = self.conn.uid("fetch", uid, "(RFC822)")
            if result != "OK":
                raise RuntimeError(f"Failed to fetch email with UID {uid}")
            email_data = data[0][1]
            email: EmailMessage = message_from_bytes(email_data, policy=policy.default)  # type: ignore
            yield uid, email
            self.last_uid = uid

    def delete(self, uid):
        logger.debug(f"Deleting email with UID {uid}")
        self.conn.uid("store", uid, "+FLAGS", "\\Deleted")
        self.conn.expunge()
