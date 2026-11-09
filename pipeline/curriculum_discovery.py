"""
Curriculum Discovery Module.
Discovers and catalogues all official CBSE Class 11 & 12 syllabi, SQPs, marking schemes,
publications, and NCERT textbook references.
"""
import requests
import urllib3
from bs4 import BeautifulSoup
import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Any

from pipeline.config import (
    CBSE_ACADEMIC_BASE,
    CBSE_CURRICULUM_2026,
    CBSE_CURRICULUM_2025,
    CBSE_SKILL_CURRICULUM,
    CBSE_SKILL_SQP,
    CBSE_CLASS12_SQP_2025,
    CBSE_PUBLICATIONS,
    NCERT_BASE,
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT_SECONDS,
    DATA_DIR,
    SUBJECT_CODE_CATALOG
)

urllib3.disable_warnings()

class CurriculumDiscovery:
    def __init__(self, logger=None):
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.verify = False

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[CurriculumDiscovery] {msg}")

    def fetch_soup(self, url: str) -> BeautifulSoup:
        self.log(f"Fetching {url}")
        resp = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def _normalize_url(self, href: str) -> str:
        href = href.strip()
        if href.startswith("http://") or href.startswith("https://"):
            return href
        return f"{CBSE_ACADEMIC_BASE}/{href.lstrip('/')}"

    def _resolve_subject(self, raw_title: str) -> Dict[str, str]:
        """Resolves subject code and standard name from title or filename."""
        clean = re.sub(r'[\r\n\t]+', ' ', raw_title).strip()
        clean = re.sub(r'\s+', ' ', clean)
        
        # Check direct match
        for name, meta in SUBJECT_CODE_CATALOG.items():
            if name.lower() == clean.lower():
                return {"name": name, "code": meta["code"], "group": meta["group"], "stream": meta["stream"]}
        
        # Check substring match
        clean_lower = clean.lower()
        best_match = None
        best_len = 0
        for name, meta in SUBJECT_CODE_CATALOG.items():
            if name.lower() in clean_lower and len(name) > best_len:
                best_match = {"name": name, "code": meta["code"], "group": meta["group"], "stream": meta["stream"]}
                best_len = len(name)
        
        if best_match:
            return best_match
            
        # Check code pattern like 843, 041, etc.
        m = re.search(r'\b(8\d{2}|0\d{2}|1\d{2}|2\d{2}|3\d{2})\b', clean)
        if m:
            code = m.group(1).zfill(3)
            for name, meta in SUBJECT_CODE_CATALOG.items():
                if meta["code"] == code:
                    return {"name": name, "code": meta["code"], "group": meta["group"], "stream": meta["stream"]}
                    
        return {"name": clean, "code": "UNKNOWN", "group": "Other", "stream": "General"}

    def discover_academic_curriculum(self, url: str, session_label: str) -> List[Dict[str, Any]]:
        """Extracts Senior Secondary Academic Electives, Languages, and Framework."""
        items = []
        try:
            soup = self.fetch_soup(url)
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                title = a.text.strip()
                if not href.lower().endswith(".pdf") or not title:
                    continue
                
                href_lower = href.lower()
                # We focus on Senior Secondary (SrSec)
                if not ("srsec" in href_lower or "senior" in href_lower or "curriculum_srsec" in href_lower):
                    continue
                if "sec/" in href_lower and not "srsec/" in href_lower:
                    continue  # skip Secondary (Class IX-X)
                    
                full_url = self._normalize_url(href)
                res_type = "syllabus"
                if "_rm.pdf" in href_lower or "readingmaterial" in href_lower:
                    res_type = "reading_material"
                elif "curriculum_srsec" in href_lower:
                    res_type = "curriculum_framework"

                subj_info = self._resolve_subject(title)
                
                # Check class target: CBSE Senior Secondary syllabi cover XI & XII
                classes = ["11", "12"]
                if "xi" in title.lower() and "xii" not in title.lower():
                    classes = ["11"]
                elif "xii" in title.lower() and "xi" not in title.lower():
                    classes = ["12"]

                items.append({
                    "title": title,
                    "subject_name": subj_info["name"],
                    "subject_code": subj_info["code"],
                    "group": subj_info["group"],
                    "stream": subj_info["stream"],
                    "classes": classes,
                    "resource_type": res_type,
                    "session": session_label,
                    "url": full_url,
                    "source": "CBSE Academic Portal",
                    "license": "Government Open Educational Data (Fair Dealing / Curriculum)",
                    "status": "discovered"
                })
        except Exception as e:
            self.log(f"Error scraping academic curriculum from {url}: {e}")
        return items

    def discover_skill_curriculum(self) -> List[Dict[str, Any]]:
        """Extracts all Senior Secondary Skill Subjects (801-848) for Classes 11 & 12."""
        items = []
        try:
            soup = self.fetch_soup(CBSE_SKILL_CURRICULUM)
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                title = a.text.strip()
                if not href.lower().endswith(".pdf") or not title:
                    continue
                href_lower = href.lower()
                if "srsec" not in href_lower:
                    continue

                full_url = self._normalize_url(href)
                filename = Path(href).name
                
                # Determine classes
                classes = ["11", "12"]
                if "_xi.pdf" in href_lower or "-xi.pdf" in href_lower or "class-xi" in href_lower:
                    classes = ["11"]
                elif "_xii.pdf" in href_lower or "-xii.pdf" in href_lower or "class-xii" in href_lower:
                    classes = ["12"]

                subj_info = self._resolve_subject(filename.replace(".pdf", ""))
                if subj_info["code"] == "UNKNOWN":
                    subj_info = self._resolve_subject(title)

                items.append({
                    "title": f"Skill Curriculum: {subj_info['name']} ({filename})",
                    "subject_name": subj_info["name"],
                    "subject_code": subj_info["code"],
                    "group": "Group-S",
                    "stream": subj_info["stream"],
                    "classes": classes,
                    "resource_type": "syllabus",
                    "session": "2026-27",
                    "url": full_url,
                    "source": "CBSE Skill Education Unit",
                    "license": "Government Open Educational Data (Fair Dealing / Curriculum)",
                    "status": "discovered"
                })
        except Exception as e:
            self.log(f"Error scraping skill curriculum: {e}")
        return items

    def discover_class12_sqp_ms(self) -> List[Dict[str, Any]]:
        """Extracts Class 12 Sample Question Papers and Marking Schemes for all subjects."""
        items = []
        try:
            soup = self.fetch_soup(CBSE_CLASS12_SQP_2025)
            rows = soup.find_all("tr")
            for tr in rows:
                cols = tr.find_all("td")
                if len(cols) < 3:
                    continue
                subj_title = cols[0].text.strip()
                if not subj_title or "Subject" in subj_title:
                    continue
                
                subj_info = self._resolve_subject(subj_title)
                
                # Check SQP link in col 1
                sqp_a = cols[1].find("a", href=True)
                if sqp_a and sqp_a["href"].lower().endswith(".pdf"):
                    items.append({
                        "title": f"Class 12 SQP: {subj_info['name']}",
                        "subject_name": subj_info["name"],
                        "subject_code": subj_info["code"],
                        "group": subj_info["group"],
                        "stream": subj_info["stream"],
                        "classes": ["12"],
                        "resource_type": "sample_question_paper",
                        "session": "2024-25",
                        "url": self._normalize_url(sqp_a["href"]),
                        "source": "CBSE Academic Portal (Examination Unit)",
                        "license": "Official CBSE Board Sample Paper",
                        "status": "discovered"
                    })
                
                # Check MS link in col 2
                ms_a = cols[2].find("a", href=True)
                if ms_a and ms_a["href"].lower().endswith(".pdf"):
                    items.append({
                        "title": f"Class 12 Marking Scheme: {subj_info['name']}",
                        "subject_name": subj_info["name"],
                        "subject_code": subj_info["code"],
                        "group": subj_info["group"],
                        "stream": subj_info["stream"],
                        "classes": ["12"],
                        "resource_type": "marking_scheme",
                        "session": "2024-25",
                        "url": self._normalize_url(ms_a["href"]),
                        "source": "CBSE Academic Portal (Examination Unit)",
                        "license": "Official CBSE Board Marking Scheme & Solutions",
                        "status": "discovered"
                    })
        except Exception as e:
            self.log(f"Error scraping Class 12 SQPs: {e}")
        return items

    def discover_skill_sqp_ms(self) -> List[Dict[str, Any]]:
        """Extracts Class 11 and Class 12 Skill Subject SQPs and Marking Schemes."""
        items = []
        try:
            soup = self.fetch_soup(CBSE_SKILL_SQP)
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href.lower().endswith(".pdf"):
                    continue
                href_lower = href.lower()
                
                classes = []
                if "sqp_ms_xi/" in href_lower:
                    classes = ["11"]
                elif "sqp_ms_xii/" in href_lower:
                    classes = ["12"]
                else:
                    continue

                res_type = "sample_question_paper" if "_sqp.pdf" in href_lower else "marking_scheme"
                filename = Path(href).name
                subj_info = self._resolve_subject(filename.replace(".pdf", ""))

                items.append({
                    "title": f"Class {'/'.join(classes)} Skill {res_type.upper()}: {subj_info['name']}",
                    "subject_name": subj_info["name"],
                    "subject_code": subj_info["code"],
                    "group": "Group-S",
                    "stream": subj_info["stream"],
                    "classes": classes,
                    "resource_type": res_type,
                    "session": "2025-26",
                    "url": self._normalize_url(href),
                    "source": "CBSE Skill Education Unit",
                    "license": "Official CBSE Skill Sample Paper / Solutions",
                    "status": "discovered"
                })
        except Exception as e:
            self.log(f"Error scraping Skill SQP/MS: {e}")
        return items

    def discover_ncert_textbooks(self) -> List[Dict[str, Any]]:
        """Catalogues standard NCERT textbooks for Class 11 and 12 core academic subjects."""
        # Standard NCERT book book-codes (Class 11: k*, Class 12: l*)
        ncert_subjects = [
            # Class 11
            {"code": "041", "subject": "Mathematics", "class": "11", "book_code": "kemh1", "chapters": 14},
            {"code": "042", "subject": "Physics", "class": "11", "book_code": "keph1", "chapters": 7},
            {"code": "042", "subject": "Physics Part 2", "class": "11", "book_code": "keph2", "chapters": 7},
            {"code": "043", "subject": "Chemistry", "class": "11", "book_code": "kech1", "chapters": 6},
            {"code": "043", "subject": "Chemistry Part 2", "class": "11", "book_code": "kech2", "chapters": 3},
            {"code": "044", "subject": "Biology", "class": "11", "book_code": "kebo1", "chapters": 19},
            {"code": "055", "subject": "Accountancy", "class": "11", "book_code": "keac1", "chapters": 8},
            {"code": "054", "subject": "Business Studies", "class": "11", "book_code": "kebs1", "chapters": 11},
            {"code": "030", "subject": "Economics (Statistics)", "class": "11", "book_code": "kest1", "chapters": 8},
            {"code": "030", "subject": "Economics (Indian Economy)", "class": "11", "book_code": "keec1", "chapters": 8},
            {"code": "083", "subject": "Computer Science", "class": "11", "book_code": "kecs1", "chapters": 11},
            {"code": "065", "subject": "Informatics Practices", "class": "11", "book_code": "keip1", "chapters": 8},
            {"code": "301", "subject": "English Core (Hornbill)", "class": "11", "book_code": "kehb1", "chapters": 8},
            {"code": "301", "subject": "English Core (Snapshots)", "class": "11", "book_code": "kesp1", "chapters": 8},

            # Class 12
            {"code": "041", "subject": "Mathematics Part 1", "class": "12", "book_code": "lemh1", "chapters": 6},
            {"code": "041", "subject": "Mathematics Part 2", "class": "12", "book_code": "lemh2", "chapters": 7},
            {"code": "042", "subject": "Physics Part 1", "class": "12", "book_code": "leph1", "chapters": 8},
            {"code": "042", "subject": "Physics Part 2", "class": "12", "book_code": "leph2", "chapters": 6},
            {"code": "043", "subject": "Chemistry Part 1", "class": "12", "book_code": "lech1", "chapters": 5},
            {"code": "043", "subject": "Chemistry Part 2", "class": "12", "book_code": "lech2", "chapters": 5},
            {"code": "044", "subject": "Biology", "class": "12", "book_code": "lebo1", "chapters": 13},
            {"code": "055", "subject": "Accountancy Part 1", "class": "12", "book_code": "leac1", "chapters": 5},
            {"code": "055", "subject": "Accountancy Part 2", "class": "12", "book_code": "leac2", "chapters": 4},
            {"code": "054", "subject": "Business Studies Part 1", "class": "12", "book_code": "lebs1", "chapters": 8},
            {"code": "054", "subject": "Business Studies Part 2", "class": "12", "book_code": "lebs2", "chapters": 4},
            {"code": "030", "subject": "Economics (Macro)", "class": "12", "book_code": "leec1", "chapters": 6},
            {"code": "030", "subject": "Economics (Micro)", "class": "12", "book_code": "leec2", "chapters": 6},
            {"code": "083", "subject": "Computer Science", "class": "12", "book_code": "lecs1", "chapters": 12},
            {"code": "065", "subject": "Informatics Practices", "class": "12", "book_code": "leip1", "chapters": 7},
            {"code": "301", "subject": "English Core (Flamingo)", "class": "12", "book_code": "lefl1", "chapters": 8},
            {"code": "301", "subject": "English Core (Vistas)", "class": "12", "book_code": "levi1", "chapters": 6}
        ]

        items = []
        for b in ncert_subjects:
            subj_meta = SUBJECT_CODE_CATALOG.get(b["subject"].split(" Part")[0], {"group": "Group-A", "stream": "Academic"})
            # Preliminary chapter 1 & full book links
            ch1_url = f"https://ncert.nic.in/textbook/pdf/{b['book_code']}01.pdf"
            items.append({
                "title": f"NCERT Textbook: Class {b['class']} {b['subject']}",
                "subject_name": b["subject"].split(" Part")[0],
                "subject_code": b["code"],
                "group": subj_meta.get("group", "Group-A"),
                "stream": subj_meta.get("stream", "Academic"),
                "classes": [b["class"]],
                "resource_type": "textbook",
                "session": "Rationalised 2024-26",
                "url": ch1_url,
                "book_code": b["book_code"],
                "chapter_count": b["chapters"],
                "source": "NCERT Official Textbook Repository",
                "license": "NCERT Educational Fair Use / Curriculum Reference",
                "status": "discovered"
            })
        return items

    def run_full_discovery(self) -> List[Dict[str, Any]]:
        self.log("Starting comprehensive CBSE Senior Secondary curriculum discovery...")
        all_resources = []
        
        # 1. 2026 Academic Curriculum
        res_2026 = self.discover_academic_curriculum(CBSE_CURRICULUM_2026, "2025-26 / 2026-27")
        self.log(f"Discovered {len(res_2026)} resources from 2026 Academic Curriculum")
        all_resources.extend(res_2026)

        # 2. 2025 Academic Curriculum
        res_2025 = self.discover_academic_curriculum(CBSE_CURRICULUM_2025, "2024-25")
        self.log(f"Discovered {len(res_2025)} resources from 2025 Academic Curriculum")
        all_resources.extend(res_2025)

        # 3. Skill Education Curricula (801-848)
        res_skill = self.discover_skill_curriculum()
        self.log(f"Discovered {len(res_skill)} resources from Skill Education Curricula")
        all_resources.extend(res_skill)

        # 4. Class 12 SQPs & Marking Schemes
        res_sqp = self.discover_class12_sqp_ms()
        self.log(f"Discovered {len(res_sqp)} resources from Class 12 SQP/MS Portal")
        all_resources.extend(res_sqp)

        # 5. Skill SQPs & Marking Schemes (Classes 11 & 12)
        res_skill_sqp = self.discover_skill_sqp_ms()
        self.log(f"Discovered {len(res_skill_sqp)} resources from Skill SQP/MS Portal")
        all_resources.extend(res_skill_sqp)

        # 6. NCERT Official Textbooks
        res_ncert = self.discover_ncert_textbooks()
        self.log(f"Discovered {len(res_ncert)} NCERT Textbook series")
        all_resources.extend(res_ncert)

        # Deduplicate by URL
        seen_urls = set()
        unique_resources = []
        for r in all_resources:
            url = r["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(r)

        self.log(f"Discovery complete! Total unique educational resources: {len(unique_resources)}")
        
        # Save Acquisition Manifest
        manifest_path = DATA_DIR / "ACQUISITION_MANIFEST.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(unique_resources, f, indent=2, ensure_ascii=False)
        self.log(f"Saved JSON manifest to {manifest_path}")

        # Also save CSV for easy data inspection
        csv_path = DATA_DIR / "ACQUISITION_MANIFEST.csv"
        if unique_resources:
            fieldnames = ["subject_code", "subject_name", "classes", "group", "stream", "resource_type", "session", "title", "url", "source", "license", "status"]
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for row in unique_resources:
                    row_copy = dict(row)
                    row_copy["classes"] = ",".join(row_copy["classes"])
                    writer.writerow(row_copy)
            self.log(f"Saved CSV manifest to {csv_path}")

        return unique_resources

if __name__ == "__main__":
    disc = CurriculumDiscovery()
    items = disc.run_full_discovery()
    print(f"Discovery test finished with {len(items)} items.")
