from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

// Fonction pour valider les numéros de téléphone (longueur entre 10 et 15)
const validatePhones = (phones) => {
  return [...new Set(phones.filter(phone => /^\d{10,15}$/.test(phone)))];
};

@app.route('/scrape', methods=['POST'])
def scrape():
    # Verify if URL is provided
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Please provide a URL.'}), 400

    url = data['url']

    try:
        # Send HTTP GET request
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text)
        emails = [email.strip().lower() for email in emails]  # Clean emails
        unique_emails = list(set(emails))  # Remove duplicates

        # Extract phone numbers
        phones = re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', soup.text)
        phones = [re.sub(r'\D', '', phone) for phone in phones]  # Clean phone numbers
        unique_phones = list(set(phones))  # Remove duplicates

        # Return results
        return jsonify({
            'emails': unique_emails,
            'phones': unique_phones
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error accessing the URL: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
