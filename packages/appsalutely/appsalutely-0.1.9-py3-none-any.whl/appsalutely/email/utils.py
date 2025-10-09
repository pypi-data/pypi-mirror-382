from email.message import EmailMessage


def forward_received_email(email: EmailMessage, from_addr: str, to_addr: str) -> None:
    try:
        email.replace_header("Reply-To", email["From"])
    except KeyError:
        email["Reply-To"] = email["From"]
    try:
        email.replace_header("From", from_addr)
    except KeyError:
        email["From"] = from_addr
    try:
        email.replace_header("To", to_addr)
    except KeyError:
        email["To"] = to_addr
    try:
        email.replace_header("CC", "")
    except KeyError:
        pass
    try:
        email.replace_header("BCC", "")
    except KeyError:
        pass


def looks_like_autoreply(email: EmailMessage):
    if "automatic reply" in email.get("Subject", "").lower():
        return True
    if email.get("X-Auto-Response-Suppress", "").lower() in (
        "all",
        "dr",
        "autoreply",
    ):
        return True
    if email.get("Auto-Submitted", "no").lower() != "no":
        return True
    return False
