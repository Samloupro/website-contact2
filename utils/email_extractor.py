import re
import json
from email_validator import validate_email, EmailNotValidError

def extract_emails_html(text):
    return re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)

def extract_emails_jsonld(soup):
    emails = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "email" in data:
                email = data["email"].strip().rstrip('.')
                try:
                    validate_email(email)
                    emails.append(email)
                except EmailNotValidError:
                    continue
        except (json.JSONDecodeError, TypeError):
            continue
    return emails
