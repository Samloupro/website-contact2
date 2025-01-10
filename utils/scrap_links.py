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

def scrape_links(url, headers):
    if not url or not is_valid_url(url):
        return {'error': 'Invalid URL provided.'}, 400

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = extract_links(soup, url)
        return links, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing the URL: {e}")
        return None, f"Error accessing the URL: {e}"
