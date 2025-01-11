from bs4 import BeautifulSoup
import requests
import logging
from utils.email_extractor import extract_emails_html, extract_emails_jsonld
from utils.phone_extractor import extract_phones_html, extract_phones_jsonld, validate_phones

logger = logging.getLogger(__name__)

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
            sub_response = requests.get(link, headers=headers, timeout=10)
            sub_response.raise_for_status()
            sub_soup = BeautifulSoup(sub_response.text, 'html.parser')

            sub_emails = extract_emails_html(sub_soup.text) + extract_emails_jsonld(sub_soup)
            for email in set(sub_emails):
                if email not in emails:
                    emails[email] = []
                emails[email].append(link)

            sub_phones = extract_phones_html(sub_soup.text) + extract_phones_jsonld(sub_soup)
            for phone in set(validate_phones(sub_phones)):
                if phone not in phones:
                    phones[phone] = []
                phones[phone].append(link)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to process link {link}: {e}")

    return emails, phones, visited_links
