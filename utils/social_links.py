import json

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
                    for key in social_links:
                        if key in link:
                            social_links[key] = link
        except (json.JSONDecodeError, TypeError):
            continue
    return social_links

