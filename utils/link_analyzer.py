# utils/link_analyzer.py

from bs4 import BeautifulSoup
import requests
import logging
from urllib.parse import urlparse
from utils.email_extractor import extract_emails_html, extract_emails_jsonld
from utils.phone_extractor import extract_phones_html, extract_phones_jsonld, validate_phones
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def analyze_links(links, headers):
    emails = {}
    phones = {}
    visited_links = set()

    for link in links:
        if link in visited_links:
            continue

        logger.info(f"Analyzing link: {link}")
        visited_links.add(link)

        try:
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            emails_found = extract_emails_html(soup.text) + extract_emails_jsonld(soup)
            for email in set(emails_found):
                email = email.strip().rstrip('.')  # Ensure no trailing dot and strip whitespace
                if validate_email_address(email):
                    emails.setdefault(email, []).append(link)

            phones_found = extract_phones_html(soup.text) + extract_phones_jsonld(soup)
            for phone in set(validate_phones(phones_found)):
                phones.setdefault(phone, []).append(link)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to process link {link}: {e}")

    return emails, phones, visited_links

def validate_email_address(email):
    try:
        email = email.strip().rstrip('.')  # Ensure no trailing dot and strip whitespace
        v = validate_email(email)
        # Ensure the email has no trailing dot or other invalid characters
        if email != v.email:
            raise EmailNotValidError("Invalid email format")
        return True
    except EmailNotValidError:
        return False
