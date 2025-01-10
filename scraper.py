from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import json

# Configuration du navigateur headless
def setup_driver():
    options = Options()
    options.add_argument('--headless')  # Exécuter sans interface graphique
    options.add_argument('--disable-gpu')  # Désactiver le GPU
    options.add_argument('--no-sandbox')  # Nécessaire pour certains environnements
    options.add_argument('--disable-dev-shm-usage')  # Résoudre les problèmes de mémoire partagée
    options.add_argument('--incognito')  # Mode incognito
    options.add_argument('log-level=3')  # Réduire les logs

    # Remplacez le chemin par celui où se trouve votre ChromeDriver
    service = Service('/path/to/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Fonction pour extraire les emails
def extract_emails(soup):
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text)
    return list(set(emails))  # Supprimer les doublons

# Fonction pour extraire les numéros de téléphone
def extract_phones(soup):
    phones = re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', soup.text)
    return list(set(phones))  # Supprimer les doublons

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

    social_patterns = {
        "facebook": r"https?://(www\.)?facebook\.com/[^\s\"']+",
        "instagram": r"https?://(www\.)?instagram\.com/[^\s\"']+",
        "twitter": r"https?://(www\.)?twitter\.com/[^\s\"']+",
        "tiktok": r"https?://(www\.)?tiktok\.com/[^\s\"']+",
        "linkedin": r"https?://(www\.)?linkedin\.com/[^\s\"']+",
        "youtube": r"https?://(www\.)?youtube\.com/[^\s\"']+",
        "pinterest": r"https?://(www\.)?pinterest\.com/[^\s\"']+",
        "github": r"https?://(www\.)?github\.com/[^\s\"']+",
        "snapchat": r"https?://(www\.)?snapchat\.com/[^\s\"']+"
    }

    for platform, pattern in social_patterns.items():
        match = re.search(pattern, soup.text)
        if match:
            social_links[platform] = match.group(0)

    return social_links

# Fonction principale
def scrape_url(url):
    driver = setup_driver()
    try:
        print(f"Fetching {url}...")
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extraire les informations
        emails = extract_emails(soup)
        phones = extract_phones(soup)
        social_links = extract_social_links(soup)

        result = {
            "emails": emails,
            "phones": phones,
            "social_links": social_links
        }
        return result

    finally:
        driver.quit()  # Fermer le navigateur

# Exemple d'utilisation
if __name__ == "__main__":
    url = "https://www.propertyfinder.ae/en/find-agent"
    result = scrape_url(url)
    print(json.dumps(result, indent=4))
