from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import uuid
import logging
from urllib.parse import urlparse
from utils.email_extractor import extract_emails_html, extract_emails_jsonld
from utils.phone_extractor import extract_phones_html, extract_phones_jsonld, validate_phones
from utils.social_links import extract_social_links_jsonld
from utils.scrap_links import scrape_links
from utils.user_agent import get_user_agent_headers
from utils.link_analyzer import analyze_links, is_valid_url, extract_links  # Import the link analyzer

app = Flask(__name__)
SCRIPT_VERSION = "V 1.3"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    headers = get_user_agent_headers()

    links, error = scrape_links(url, headers)
    if error:
        return jsonify({'error': error}), 500

    domain = urlparse(url).netloc
    emails, phones, visited_links = analyze_links(links, headers, domain)

    social_links = extract_social_links_jsonld(BeautifulSoup(requests.get(url, headers=headers, timeout=10).text, 'html.parser'))

    result = {
        "request_id": str(uuid.uuid4()),
        "domain": url.split("//")[-1].split("/")[0],
        "query": url,
        "status": "OK",
        "data": [
            {
                "emails": [{"value": email, "sources": sources} for email, sources in emails.items()],
                "phone_numbers": [{"value": phone, "sources": sources} for phone, sources in phones.items()],
                "social_links": {
                    "facebook": social_links.get("facebook"),
                    "github": social_links.get("github"),
                    "instagram": social_links.get("instagram"),
                    "linkedin": social_links.get("linkedin"),
                    "pinterest": social_links.get("pinterest"),
                    "snapchat": social_links.get("snapchat"),
                    "tiktok": social_links.get("tiktok"),
                    "twitter": social_links.get("twitter"),
                    "youtube": social_links.get("youtube")
                },
                "unique_links": sorted(list(visited_links))  # Add unique links to the result in alphabetical order
            }
        ]
    }

    logger.info(f"Processed URL: {url}")
    return jsonify(result)

if __name__ == '__main__':
    print(f"Starting script version: {SCRIPT_VERSION}")
    app.run(host='0.0.0.0', port=5000)
