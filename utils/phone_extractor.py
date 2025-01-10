import re
import json

def validate_phones(phones):
    valid_phones = []
    for phone in phones:
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check the length
        if 8 <= len(digits_only) <= 15:
            # Check for E.164 compliance
            if re.match(r'^\+\d{1,15}$', phone):
                valid_phones.append(phone)
    return valid_phones

def extract_phones_html(text):
    """
    Extract phone numbers from HTML text using regex.
    """
    return re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', text)

def extract_phones_jsonld(soup):
    """
    Extract phone numbers from JSON-LD scripts in the HTML soup.
    """
    phones = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "telephone" in data:
                phones.append(data["telephone"])
        except (json.JSONDecodeError, TypeError) as e:
            # Log the error or handle it appropriately
            continue
    return phones
