import re

def validate_phones(phones):
    return [phone for phone in phones if 10 <= len(re.sub(r'\D', '', phone)) <= 15]

def extract_phones_html(text):
    return re.findall(r'\+?[0-9][0-9.\-\s()]{8,}[0-9]', text)

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
