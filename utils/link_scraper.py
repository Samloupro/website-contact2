from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import logging
import json

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

def extract_links_jsonld(soup):
    links = set()
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "sameAs" in data:
                for link in data["sameAs"]:
                    if link.startswith("http"):
                        links.add(link)
        except (json.JSONDecodeError, TypeError):
            continue
    return links

def link_scraper(url, headers):
    if not url or not is_valid_url(url):
        return {'error': 'Invalid URL provided.'}, 400

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        links = extract_links(soup, url)
        jsonld_links = extract_links_jsonld(soup)
        all_links = links.union(jsonld_links)  # Combine both sets of links

        # Ajoutez des logs pour vérifier les liens extraits
        logger.info(f"Extracted links: {all_links}")

        return list(all_links), None
    except requests.RequestException as e:
        logger.error(f"Error scraping {url}: {e}")
        return [], str(e)
