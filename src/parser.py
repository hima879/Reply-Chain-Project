"""
Day 1 - Email parser
--------------------
Goal: turn a raw email (.eml file) into a small, clean Python object (Msg)
that the rest of the project can easily use.

Why do we need this?
A raw email is just messy text full of headers. Our detector needs to ask
simple questions like "who sent this?" or "what links are inside?".
The parser answers those questions once, so later steps stay simple.
"""
import re
from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, getaddresses

# Finds links such as http://bit.ly/abc inside the body text
URL_PATTERN = re.compile(r"https?://[^\s<>\"')]+", re.I)


@dataclass
class Msg:
    """One parsed email. Every field is something a detector rule may need."""
    sender: str = ""            # priya@kestrelfoods.com
    sender_name: str = ""       # Priya Nair
    reply_to: str = ""          # where replies would really go (attackers often change this)
    recipients: list = field(default_factory=list)
    subject: str = ""
    date: str = ""
    message_id: str = ""        # unique id of this email
    in_reply_to: str = ""       # id of the email this one replies to (thread link)
    auth_results: str = ""      # SPF / DKIM / DMARC results added by the mail server
    body: str = ""              # only the NEW text (old quoted text removed)
    urls: list = field(default_factory=list)
    attachments: list = field(default_factory=list)

    @property
    def sender_domain(self) -> str:
        """kestrelfoods.com from priya@kestrelfoods.com"""
        return self.sender.rsplit("@", 1)[-1] if "@" in self.sender else ""


def remove_quoted_text(text: str) -> str:
    """Replies often repeat old emails ('> old text'). Keep only the new part."""
    new_lines = []
    for line in text.splitlines():
        if re.match(r"^\s*On .{5,120} wrote:\s*$", line):   # 'On Mon, X wrote:' marks old text
            break
        if line.lstrip().startswith(">"):                    # '>' lines are quoted old text
            continue
        new_lines.append(line)
    return "\n".join(new_lines).strip()


def parse_message(raw) -> Msg:
    """Take raw email (bytes or text) and return a Msg."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8", errors="replace")
    email_obj = BytesParser(policy=policy.default).parsebytes(raw)

    # --- headers: who, to whom, about what
    name, address = parseaddr(str(email_obj.get("From", "")))
    _, reply_to = parseaddr(str(email_obj.get("Reply-To", "")))
    to_and_cc = email_obj.get_all("To", []) + email_obj.get_all("Cc", [])
    recipients = [a.lower() for _, a in getaddresses([str(h) for h in to_and_cc]) if a]

    # --- body: take the plain-text part
    body = ""
    for part in email_obj.walk():
        if part.get_content_type() == "text/plain" and not part.get_filename():
            body = part.get_content()
            break
    body = remove_quoted_text(body)

    # --- attachments: just their file names for now
    attachments = [p.get_filename() for p in email_obj.walk() if p.get_filename()]

    return Msg(
        sender=address.lower(),
        sender_name=name.strip(),
        reply_to=reply_to.lower(),
        recipients=recipients,
        subject=str(email_obj.get("Subject", "")).strip(),
        date=str(email_obj.get("Date", "")),
        message_id=str(email_obj.get("Message-ID", "")).strip("<>").lower(),
        in_reply_to=str(email_obj.get("In-Reply-To", "")).strip("<>").lower(),
        auth_results=" ".join(str(h) for h in email_obj.get_all("Authentication-Results", [])),
        body=body,
        urls=list(dict.fromkeys(URL_PATTERN.findall(body))),   # unique links, same order
        attachments=attachments,
    )


# Quick self-test: run `python src/parser.py path/to/email.eml`
if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "samples/2_hijacked_bank_change/04.eml"
    with open(path, "rb") as f:
        m = parse_message(f.read())
    print("From        :", m.sender_name, "<" + m.sender + ">")
    print("Domain      :", m.sender_domain)
    print("Reply-To    :", m.reply_to or "(none)")
    print("Subject     :", m.subject)
    print("Attachments :", m.attachments)
    print("Links       :", m.urls)
    print("Auth results:", m.auth_results)
    print("Body        :\n" + m.body)
