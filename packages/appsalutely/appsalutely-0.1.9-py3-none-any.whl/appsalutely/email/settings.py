from pydantic import BaseModel, SecretStr


class ConnectionSettings(BaseModel):
    """
    Settings for the email protocol.
    This class defines the configuration for connecting to an email server.
    Used for both SMTP and IMAP protocols.
    """

    model_config = {"extra": "forbid"}

    host: str
    port: int
    starttls: bool
    username: str
    password: SecretStr
