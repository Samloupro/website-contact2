from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def extract_links(soup, base_url):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("/"):
            href = base_url.rstrip("/") + href
        if href.startswith("http"):
            links.add(href)
    return links

def analyze_links(links, headers, domain):
    emails = {}
    phones = {}
    visited_links = set()

    for link in links:  # Analyze all links
        if link in visited_links or urlparse(link).netloc != domain:
            continue
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
            continue
    return emails, phones, visited_links
