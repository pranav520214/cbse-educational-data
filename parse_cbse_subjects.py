import json

with open('curriculum_catalog_raw.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

items = d['2026']['academic_electives'] + d['2026']['general_and_internal'] + d['2026']['languages']
print(f"Total SrSec subjects in 2026 catalog: {len(items)}")
for idx, i in enumerate(items, 1):
    print(f"{idx:02d}. {i['subject_name']} -> {i['pdf_url']}")
