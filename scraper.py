from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import json

app = Flask(__name__)

# Fonction pour valider les numéros de téléphone (longueur entre 10 et 15)
def validate_phones(phones):
    return [phone for phone in phones if 10 <= len(re.sub(r'\D', '', phone)) <= 15]

# Fonction pour extraire les liens des réseaux sociaux
def extract_social_links(soup):
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

    # Rechercher les balises <script type="application/ld+json">
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

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraire les emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text)
        emails = [email.strip().lower() for email in emails]
        unique_emails = list(set(emails))

        # Extraire et valider les numéros de téléphone
        phones = re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', soup.text)
        phones = [re.sub(r'\D', '', phone) for phone in phones]
        unique_phones = validate_phones(phones)

        # Extraire les liens des réseaux sociaux
        social_links = extract_social_links(soup)

        return jsonify({
            'emails': unique_emails,
            'phones': unique_phones,
            'social_links': social_links
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error accessing the URL: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
