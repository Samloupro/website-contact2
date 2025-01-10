from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

# Fonction pour valider les numéros de téléphone (longueur entre 10 et 15)
def validate_phones(phones):
    return list(set([phone for phone in phones if 10 <= len(phone) <= 15]))

# Fonction pour extraire les réseaux sociaux
def extract_social_links(soup):
    social_links = {
        "facebook": None,
        "instagram": None,
        "tiktok": None,
        "snapchat": None,
        "twitter": None,
        "linkedin": None,
        "github": None,
        "youtube": None,
        "pinterest": None
    }

    # URL patterns pour chaque réseau social
    patterns = {
        "facebook": r"https?://(www\.)?facebook\.com/[^\s]+",
        "instagram": r"https?://(www\.)?instagram\.com/[^\s]+",
        "tiktok": r"https?://(www\.)?tiktok\.com/@[^\s]+",
        "snapchat": r"https?://(www\.)?snapchat\.com/add/[^\s]+",
        "twitter": r"https?://(www\.)?twitter\.com/[^\s]+",
        "linkedin": r"https?://(www\.)?linkedin\.com/[^\s]+",
        "github": r"https?://(www\.)?github\.com/[^\s]+",
        "youtube": r"https?://(www\.)?(youtube\.com|youtu\.be)/[^\s]+",
        "pinterest": r"https?://(www\.)?pinterest\.com/[^\s]+"
    }

    # Rechercher les liens dans tout le texte de la page
    for platform, pattern in patterns.items():
        match = re.search(pattern, soup.text)
        if match:
            social_links[platform] = match.group(0)

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
