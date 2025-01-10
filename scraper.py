from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import json
import uuid

app = Flask(__name__)

# Version du script
SCRIPT_VERSION = "V 1.3"

# Fonction pour valider les numéros de téléphone (longueur entre 10 et 15)
def validate_phones(phones):
    return [phone for phone in phones if 10 <= len(re.sub(r'\D', '', phone)) <= 15]

# Fonction pour extraire les emails via JSON-LD
def extract_emails_jsonld(soup):
    emails = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "email" in data:
                emails.append(data["email"])
        except (json.JSONDecodeError, TypeError):
            continue
    return emails

# Fonction pour extraire les numéros de téléphone via JSON-LD
def extract_phones_jsonld(soup):
    phones = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "telephone" in data:
                phones.append(data["telephone"])
        except (json.JSONDecodeError, TypeError):
            continue
    return phones

# Fonction pour extraire les liens des réseaux sociaux via JSON-LD
def extract_social_links_jsonld(soup):
    social_links = {
        "facebook": None,
        "instagram": None,
        "twitter": None,
        "tiktok": None,
        "linkedin": None,
        "youtube": None,
        "pinterest": None,
        "github": None,
        "snapchat": None
    }

    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "sameAs" in data:
                for link in data["sameAs"]:
                    if "facebook.com" in link:
                        social_links["facebook"] = link
                    elif "instagram.com" in link:
                        social_links["instagram"] = link
                    elif "twitter.com" in link:
                        social_links["twitter"] = link
                    elif "tiktok.com" in link:
                        social_links["tiktok"] = link
                    elif "linkedin.com" in link:
                        social_links["linkedin"] = link
                    elif "youtube.com" in link:
                        social_links["youtube"] = link
                    elif "pinterest.com" in link:
                        social_links["pinterest"] = link
                    elif "github.com" in link:
                        social_links["github"] = link
                    elif "snapchat.com" in link:
                        social_links["snapchat"] = link
        except (json.JSONDecodeError, TypeError):
            continue

    return social_links

# Fonction pour explorer tous les liens sur la page (limité à une profondeur donnée)
def extract_links(soup, base_url, max_links=50):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        if len(links) >= max_links:
            break
        href = a_tag["href"]
        if href.startswith("/"):
            href = base_url.rstrip("/") + href
        if href.startswith("http"):
            links.add(href)
    return links

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Please provide a URL.'}), 400

    url = data['url']

    # Ajouter les headers ici
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraire tous les liens
        links = extract_links(soup, url)

        # Initialiser les résultats
        emails = {}
        phones = {}
        social_links = extract_social_links_jsonld(soup)

        # Scraper chaque lien
        for link in links:
            try:
                sub_response = requests.get(link, headers=headers, timeout=10)
                sub_response.raise_for_status()
                sub_soup = BeautifulSoup(sub_response.text, 'html.parser')

                # Extraire les emails
                sub_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', sub_soup.text)
                sub_emails.extend(extract_emails_jsonld(sub_soup))
                for email in set(sub_emails):
                    if email not in emails:
                        emails[email] = []
                    emails[email].append(link)

                # Extraire les numéros de téléphone
                sub_phones = re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', sub_soup.text)
                sub_phones.extend(extract_phones_jsonld(sub_soup))
                for phone in set(validate_phones(sub_phones)):
                    if phone not in phones:
                        phones[phone] = []
                    phones[phone].append(link)

            except requests.exceptions.RequestException:
                continue

        # Organiser les résultats
        result = {
            "status": "OK",
            "request_id": str(uuid.uuid4()),
            "data": [
                {
                    "domain": url.split("//")[-1].split("/")[0],
                    "query": url,
                    "emails": [{"value": email, "sources": sources} for email, sources in emails.items()],
                    "phone_numbers": [{"value": phone, "sources": sources} for phone, sources in phones.items()],
                    **social_links
                }
            ]
        }

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error accessing the URL: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"Starting script version: {SCRIPT_VERSION}")
    app.run(host='0.0.0.0', port=5000)
