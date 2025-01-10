import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import uuid
import logging
from urllib.parse import urlparse
from utils.email_extractor import extract_emails_html, extract_emails_jsonld
from utils.phone_extractor import extract_phones_html, extract_phones_jsonld, validate_phones
from utils.social_links import extract_social_links_jsonld
from utils.link_scraper import scrape_links
from utils.user_agent import get_user_agent_headers
from utils.link_analyzer import analyze_links, is_valid_url, extract_links
import requests

app = Flask(__name__)
SCRIPT_VERSION = "V 1.3"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_links_parallel(links, headers, domain):
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, analyze_links, link, headers, domain)
            for link in links
        ]
        results = loop.run_until_complete(asyncio.gather(*tasks))
    return results

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    headers = get_user_agent_headers()

    include_emails = request.args.get('include_emails', 'true').lower() == 'true'
    include_phones = request.args.get('include_phones', 'true').lower() == 'true'
    include_social_links = request.args.get('include_social_links', 'true').lower() == 'true'
    include_unique_links = request.args.get('include_unique_links', 'true').lower() == 'true'

    links, error = scrape_links(url, headers)
    if error:
        return jsonify({'error': error}), 500

    domain = urlparse(url).netloc

    emails, phones, visited_links = {}, {}, set()
    if include_emails or include_phones or include_unique_links:
        results = analyze_links_parallel(links, headers, domain)
        for result in results:
            emails.update(result[0])
            phones.update(result[1])
            visited_links.update(result[2])

    social_links = {}
    if include_social_links:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            social_links = extract_social_links_jsonld(soup)
        else:
            return jsonify({'error': 'Failed to fetch the URL'}), 500

    result = {
        "request_id": str(uuid.uuid4()),
        "domain": url.split("//")[-1].split("/")[0],
        "query": url,
        "status": "OK",
        "data": [
            {
                "emails": [{"value": email, "sources": sources} for email, sources in emails.items()] if include_emails else [],
                "phone_numbers": [{"value": phone, "sources": sources} for phone, sources in phones.items()] if include_phones else [],
                "social_links": social_links if include_social_links else {},
                "unique_links": sorted(list(visited_links)) if include_unique_links else []
            }
        ]
    }

    logger.info(f"Processed URL: {url}")
    return jsonify(result)

if __name__ == '__main__':
    print(f"Starting script version: {SCRIPT_VERSION}")
    app.run(host='0.0.0.0', port=5000)
