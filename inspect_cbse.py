import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')

def parse_senior_secondary(url, session_name):
    soup = get_soup(url)
    data = {
        'session': session_name,
        'source_url': url,
        'languages': [],
        'academic_electives': [],
        'skill_subjects': [],
        'general_and_internal': []
    }
    
    # In CBSE curriculum pages, tabs or accordions contain sections:
    # Languages, Academic Electives, Skill Subjects
    # Let's inspect all tables and lists
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.text.strip()
        if not href.lower().endswith('.pdf') or not text:
            continue
        
        full_url = href if href.startswith('http') else f"https://cbseacademic.nic.in/{href.lstrip('/')}"
        
        # Check context
        parent_text = ""
        p = a.parent
        for _ in range(3):
            if p:
                if p.get('id'):
                    parent_text += " " + p.get('id')
                parent_text += " " + (p.get('class', [''])[0] if isinstance(p.get('class'), list) else str(p.get('class', '')))
                p = p.parent
        
        item = {
            'subject_name': text,
            'pdf_url': full_url,
            'rel_path': href,
            'context': parent_text.strip()
        }
        
        # categorize
        href_lower = href.lower()
        if 'srsec' in href_lower or 'srsecondary' in href_lower or 'senior' in href_lower or 'main-senior' in href_lower:
            if 'language' in href_lower or 'lang' in href_lower:
                data['languages'].append(item)
            elif 'skill' in href_lower:
                data['skill_subjects'].append(item)
            elif any(g in href_lower for g in ['initial', 'curriculum_srsec', 'general']):
                data['general_and_internal'].append(item)
            else:
                data['academic_electives'].append(item)
        elif 'curriculummain' in href_lower:
            # Check text or path
            if 'sec/' in href_lower:
                continue # secondary (9-10)
            data['academic_electives'].append(item)

    return data

if __name__ == '__main__':
    catalog = {}
    for year, name in [('2026', '2025-26 / 2026-27'), ('2025', '2024-25')]:
        u = f'https://cbseacademic.nic.in/curriculum_{year}.html'
        print(f"Scraping {u}...")
        try:
            catalog[year] = parse_senior_secondary(u, name)
            print(f"  Languages: {len(catalog[year]['languages'])}")
            print(f"  Academic Electives: {len(catalog[year]['academic_electives'])}")
            print(f"  Skill Subjects: {len(catalog[year]['skill_subjects'])}")
            print(f"  General/Internal: {len(catalog[year]['general_and_internal'])}")
        except Exception as e:
            print(f"  Failed: {e}")

    with open('curriculum_catalog_raw.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    print("Saved curriculum_catalog_raw.json")
