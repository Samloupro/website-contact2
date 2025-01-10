from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

# Fonction pour valider les numéros de téléphone (longueur entre 10 et 15)
def validate_phones(phones):
    return [phone for phone in phones if 10 <= len(phone) <= 15]

# Fonction pour extraire les liens des réseaux sociaux
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

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "facebook.com" in href:
            social_links["facebook"] = href
        elif "instagram.com" in href:
            social_links["instagram"] = href
        elif "tiktok.com" in href:
            social_links["tiktok"] = href
        elif "snapchat.com" in href:
            social_links["snapchat"] = href
        elif "twitter.com" in href:
            social_links["twitter"] = href
        elif "linkedin.com" in href:
            social_links["linkedin"] = href
        elif "github.com" in href:
            social_links["github"] = href
        elif "youtube.com" in href or "youtu.be" in href:
            social_links["youtube"] = href
        elif "pinterest.com" in href:
            social_links["pinterest"] = href

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
