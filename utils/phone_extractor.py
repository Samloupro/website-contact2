import re
import json

def validate_phones(phones):
    valid_phone_pattern = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    return [phone for phone in phones if valid_phone_pattern.match(phone)]

def extract_phones_html(text):
    phone_pattern = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    phones = phone_pattern.findall(text)
    return phones

def extract_phones_jsonld(soup):
    phones = set()
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "telephone" in data:
                phone = data["telephone"]
                if re.match(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', phone):
                    phones.add(phone)
        except (json.JSONDecodeError, TypeError):
            continue
    return list(phones)
