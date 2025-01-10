from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import json

app = Flask(__name__)

# Version du script
SCRIPT_VERSION = "V 1.1"

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
        # Inclure les headers dans la requête
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraire les emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text)
        emails.extend(extract_emails_jsonld(soup))
        emails = [email.strip().lower() for email in emails]
        unique_emails = list(set(emails))

        # Extraire et valider les numéros de téléphone
        phones = re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', soup.text)
        phones.extend(extract_phones_jsonld(soup))
        phones = [re.sub(r'\D', '', phone) for phone in phones]
        unique_phones = validate_phones(phones)

        # Extraire les liens des réseaux sociaux
        social_links = extract_social_links_jsonld(soup)

        return jsonify({
            'version': SCRIPT_VERSION,
            'emails': unique_emails,
            'phones': unique_phones,
            'social_links': social_links
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error accessing the URL: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"Starting script version: {SCRIPT_VERSION}")
    app.run(host='0.0.0.0', port=5000)
