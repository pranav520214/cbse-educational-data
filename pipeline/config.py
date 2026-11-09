"""
Configuration module for CBSE Educational Data Acquisition Pipeline.
Defines base URLs, paths, session identifiers, subject mappings, and crawler options.
"""
import os
from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "CBSE-EDUCATIONAL-DATA"
CLASS_11_DIR = DATA_DIR / "CLASS_11"
CLASS_12_DIR = DATA_DIR / "CLASS_12"
CACHE_DIR = ROOT_DIR / "temp_raw_cache"
LOGS_DIR = ROOT_DIR / "logs"

# Ensure runtime directories exist
for p in [DATA_DIR, CLASS_11_DIR, CLASS_12_DIR, CACHE_DIR, LOGS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Academic Sessions
ACADEMIC_SESSIONS = {
    "PRIMARY_CURRICULUM": "2025-26 / 2026-27",
    "SECONDARY_CURRICULUM": "2024-25",
    "ASSESSMENT_BASELINE": "2024-25"
}

# Network and Crawler Settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Educational-AI-Research"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
}
REQUEST_TIMEOUT_SECONDS = 25
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 1.5
RATE_LIMIT_DELAY = 0.5  # seconds between downloads to respect server limits

# Official CBSE Academic Endpoints
CBSE_ACADEMIC_BASE = "https://cbseacademic.nic.in"
CBSE_CURRICULUM_2026 = f"{CBSE_ACADEMIC_BASE}/curriculum_2026.html"
CBSE_CURRICULUM_2025 = f"{CBSE_ACADEMIC_BASE}/curriculum_2025.html"
CBSE_SKILL_CURRICULUM = f"{CBSE_ACADEMIC_BASE}/skill-education-curriculum.html"
CBSE_SKILL_SQP = f"{CBSE_ACADEMIC_BASE}/skill-education-sqp.html"
CBSE_CLASS12_SQP_2025 = f"{CBSE_ACADEMIC_BASE}/SQP_CLASSXII_2024-25.html"
CBSE_PUBLICATIONS = f"{CBSE_ACADEMIC_BASE}/publication_sqps.html"

# NCERT Endpoints
NCERT_BASE = "https://ncert.nic.in"
NCERT_TEXTBOOK_BASE = f"{NCERT_BASE}/textbook/pdf"

# Master CBSE Senior Secondary Subject Codes (Official Reference Mapping)
SUBJECT_CODE_CATALOG = {
    # Core Languages (Group-L)
    "English Core": {"code": "301", "group": "Group-L", "stream": "Languages"},
    "English Elective": {"code": "001", "group": "Group-L", "stream": "Languages"},
    "Hindi Core": {"code": "302", "group": "Group-L", "stream": "Languages"},
    "Hindi Elective": {"code": "002", "group": "Group-L", "stream": "Languages"},
    "Sanskrit Core": {"code": "322", "group": "Group-L", "stream": "Languages"},
    "Sanskrit Elective": {"code": "022", "group": "Group-L", "stream": "Languages"},
    "Urdu Core": {"code": "303", "group": "Group-L", "stream": "Languages"},
    "Urdu Elective": {"code": "003", "group": "Group-L", "stream": "Languages"},
    "Arabic": {"code": "016", "group": "Group-L", "stream": "Languages"},
    "Assamese": {"code": "114", "group": "Group-L", "stream": "Languages"},
    "Bengali": {"code": "105", "group": "Group-L", "stream": "Languages"},
    "Bhoti": {"code": "194", "group": "Group-L", "stream": "Languages"},
    "Bhutia": {"code": "195", "group": "Group-L", "stream": "Languages"},
    "Bodo": {"code": "192", "group": "Group-L", "stream": "Languages"},
    "French": {"code": "118", "group": "Group-L", "stream": "Languages"},
    "German": {"code": "120", "group": "Group-L", "stream": "Languages"},
    "Gujarati": {"code": "110", "group": "Group-L", "stream": "Languages"},
    "Japanese": {"code": "194", "group": "Group-L", "stream": "Languages"},
    "Kannada": {"code": "115", "group": "Group-L", "stream": "Languages"},
    "Kashmiri": {"code": "197", "group": "Group-L", "stream": "Languages"},
    "Kokborok": {"code": "191", "group": "Group-L", "stream": "Languages"},
    "Lepcha": {"code": "126", "group": "Group-L", "stream": "Languages"},
    "Limboo": {"code": "125", "group": "Group-L", "stream": "Languages"},
    "Malayalam": {"code": "112", "group": "Group-L", "stream": "Languages"},
    "Manipuri": {"code": "111", "group": "Group-L", "stream": "Languages"},
    "Marathi": {"code": "109", "group": "Group-L", "stream": "Languages"},
    "Mizo": {"code": "198", "group": "Group-L", "stream": "Languages"},
    "Nepali": {"code": "124", "group": "Group-L", "stream": "Languages"},
    "Odia": {"code": "113", "group": "Group-L", "stream": "Languages"},
    "Persian": {"code": "023", "group": "Group-L", "stream": "Languages"},
    "Punjabi": {"code": "104", "group": "Group-L", "stream": "Languages"},
    "Russian": {"code": "021", "group": "Group-L", "stream": "Languages"},
    "Sindhi": {"code": "108", "group": "Group-L", "stream": "Languages"},
    "Spanish": {"code": "196", "group": "Group-L", "stream": "Languages"},
    "Tamil": {"code": "106", "group": "Group-L", "stream": "Languages"},
    "Tangkhul": {"code": "193", "group": "Group-L", "stream": "Languages"},
    "Telugu AP": {"code": "107", "group": "Group-L", "stream": "Languages"},
    "Telugu Telangana": {"code": "189", "group": "Group-L", "stream": "Languages"},
    "Tibetan": {"code": "117", "group": "Group-L", "stream": "Languages"},

    # Science Electives (Group-A)
    "Mathematics": {"code": "041", "group": "Group-A", "stream": "Science / Commerce"},
    "Applied Mathematics": {"code": "241", "group": "Group-A", "stream": "Commerce / Humanities / Science"},
    "Physics": {"code": "042", "group": "Group-A", "stream": "Science"},
    "Chemistry": {"code": "043", "group": "Group-A", "stream": "Science"},
    "Biology": {"code": "044", "group": "Group-A", "stream": "Science"},
    "Bio Technology": {"code": "045", "group": "Group-A", "stream": "Science"},

    # Commerce Electives (Group-A)
    "Accountancy": {"code": "055", "group": "Group-A", "stream": "Commerce"},
    "Business Studies": {"code": "054", "group": "Group-A", "stream": "Commerce"},
    "Economics": {"code": "030", "group": "Group-A", "stream": "Commerce / Humanities"},
    "Entrepreneurship": {"code": "066", "group": "Group-A", "stream": "Commerce / Elective"},

    # Humanities / Social Science Electives (Group-A)
    "History": {"code": "027", "group": "Group-A", "stream": "Humanities"},
    "Political Science": {"code": "028", "group": "Group-A", "stream": "Humanities"},
    "Geography": {"code": "029", "group": "Group-A", "stream": "Humanities"},
    "Psychology": {"code": "037", "group": "Group-A", "stream": "Humanities"},
    "Sociology": {"code": "039", "group": "Group-A", "stream": "Humanities"},
    "Legal Studies": {"code": "074", "group": "Group-A", "stream": "Humanities / Elective"},
    "Knowledge Tradition - Practices India": {"code": "073", "group": "Group-A", "stream": "Humanities / Elective"},

    # Computing & Technical Electives (Group-A)
    "Computer Science": {"code": "083", "group": "Group-A", "stream": "Science / Computing"},
    "Infomatics Practices": {"code": "065", "group": "Group-A", "stream": "Computing / Commerce"},
    "Informatics Practices": {"code": "065", "group": "Group-A", "stream": "Computing / Commerce"},
    "Engineering Graphics": {"code": "046", "group": "Group-A", "stream": "Science / Technical"},

    # Performing & Visual Arts, Physical Education (Group-A)
    "Fine Arts": {"code": "049", "group": "Group-A", "stream": "Visual Arts"},
    "Painting": {"code": "049", "group": "Group-A", "stream": "Visual Arts"},
    "Graphics": {"code": "050", "group": "Group-A", "stream": "Visual Arts"},
    "Sculpture": {"code": "051", "group": "Group-A", "stream": "Visual Arts"},
    "Applied Arts": {"code": "052", "group": "Group-A", "stream": "Visual Arts"},
    "Dance": {"code": "056", "group": "Group-A", "stream": "Performing Arts"},
    "Carnatic Vocal": {"code": "031", "group": "Group-A", "stream": "Performing Arts"},
    "Carnatic Melodic": {"code": "032", "group": "Group-A", "stream": "Performing Arts"},
    "Carnatic Percussion": {"code": "033", "group": "Group-A", "stream": "Performing Arts"},
    "Hindustani Vocal": {"code": "034", "group": "Group-A", "stream": "Performing Arts"},
    "Hindustani Melodic": {"code": "035", "group": "Group-A", "stream": "Performing Arts"},
    "Hindustani Percussion": {"code": "036", "group": "Group-A", "stream": "Performing Arts"},
    "Home Science": {"code": "064", "group": "Group-A", "stream": "Interdisciplinary"},
    "Physical Education": {"code": "048", "group": "Group-A", "stream": "Physical Education"},
    "NCC": {"code": "076", "group": "Group-A", "stream": "General / Defense"},

    # General & Compulsory Internal Subjects
    "Health and Physical Education": {"code": "500", "group": "Internal", "stream": "Compulsory"},
    "Work Experience": {"code": "501", "group": "Internal", "stream": "Compulsory"},
    "General Studies": {"code": "502", "group": "Internal", "stream": "Compulsory"},
    "Introduction to Senior Secondary Curriculum": {"code": "000", "group": "Curriculum-Framework", "stream": "Mandatory Framework"},

    # Skill Electives (Group-S)
    "Retail": {"code": "801", "group": "Group-S", "stream": "Skill / Management"},
    "Information Technology": {"code": "802", "group": "Group-S", "stream": "Skill / Computing"},
    "Web Application": {"code": "803", "group": "Group-S", "stream": "Skill / Computing"},
    "Automotive": {"code": "804", "group": "Group-S", "stream": "Skill / Engineering"},
    "Financial Markets Management": {"code": "805", "group": "Group-S", "stream": "Skill / Finance"},
    "Tourism": {"code": "806", "group": "Group-S", "stream": "Skill / Hospitality"},
    "Beauty & Wellness": {"code": "807", "group": "Group-S", "stream": "Skill / Personal Care"},
    "Agriculture": {"code": "808", "group": "Group-S", "stream": "Skill / Agriculture"},
    "Food Production": {"code": "809", "group": "Group-S", "stream": "Skill / Hospitality"},
    "Front Office Operations": {"code": "810", "group": "Group-S", "stream": "Skill / Hospitality"},
    "Banking": {"code": "811", "group": "Group-S", "stream": "Skill / Finance"},
    "Marketing": {"code": "812", "group": "Group-S", "stream": "Skill / Management"},
    "Health Care": {"code": "813", "group": "Group-S", "stream": "Skill / Healthcare"},
    "Insurance": {"code": "814", "group": "Group-S", "stream": "Skill / Finance"},
    "Horticulture": {"code": "816", "group": "Group-S", "stream": "Skill / Agriculture"},
    "Typography & Computer Applications": {"code": "817", "group": "Group-S", "stream": "Skill / Office"},
    "Geospatial Technology": {"code": "818", "group": "Group-S", "stream": "Skill / Tech"},
    "Electrical Technology": {"code": "819", "group": "Group-S", "stream": "Skill / Engineering"},
    "Electronics Technology": {"code": "820", "group": "Group-S", "stream": "Skill / Engineering"},
    "Multi-Media": {"code": "821", "group": "Group-S", "stream": "Skill / Media"},
    "Taxation": {"code": "822", "group": "Group-S", "stream": "Skill / Finance"},
    "Cost Accounting": {"code": "823", "group": "Group-S", "stream": "Skill / Finance"},
    "Office Procedures and Practices": {"code": "824", "group": "Group-S", "stream": "Skill / Office"},
    "Shorthand (English)": {"code": "825", "group": "Group-S", "stream": "Skill / Office"},
    "Shorthand (Hindi)": {"code": "826", "group": "Group-S", "stream": "Skill / Office"},
    "Air-Conditioning & Refrigeration": {"code": "827", "group": "Group-S", "stream": "Skill / Engineering"},
    "Medical Diagnostics": {"code": "828", "group": "Group-S", "stream": "Skill / Healthcare"},
    "Textile Design": {"code": "829", "group": "Group-S", "stream": "Skill / Design"},
    "Design": {"code": "830", "group": "Group-S", "stream": "Skill / Design"},
    "Salesmanship": {"code": "831", "group": "Group-S", "stream": "Skill / Management"},
    "Business Administration": {"code": "833", "group": "Group-S", "stream": "Skill / Management"},
    "Food, Nutrition & Dietetics": {"code": "834", "group": "Group-S", "stream": "Skill / Nutrition"},
    "Mass Media Studies": {"code": "835", "group": "Group-S", "stream": "Skill / Media"},
    "Library & Information Science": {"code": "836", "group": "Group-S", "stream": "Skill / Information"},
    "Fashion Studies": {"code": "837", "group": "Group-S", "stream": "Skill / Design"},
    "Yoga": {"code": "841", "group": "Group-S", "stream": "Skill / Wellness"},
    "Early Childhood Care & Education": {"code": "842", "group": "Group-S", "stream": "Skill / Education"},
    "Artificial Intelligence": {"code": "843", "group": "Group-S", "stream": "Skill / Emerging Tech"},
    "Data Science": {"code": "844", "group": "Group-S", "stream": "Skill / Emerging Tech"},
    "Physical Activity Trainer": {"code": "845", "group": "Group-S", "stream": "Skill / Sports"},
    "Land Transportation Associate": {"code": "846", "group": "Group-S", "stream": "Skill / Logistics"},
    "Electronics & Hardware": {"code": "847", "group": "Group-S", "stream": "Skill / Engineering"},
    "Design Thinking & Innovation": {"code": "848", "group": "Group-S", "stream": "Skill / Innovation"}
}
