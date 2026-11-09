"""
Subject Extractor and Inventory Builder.
Partitions the discovered acquisition manifest into Class 11 and Class 12 inventories,
builds the canonical subject directories, and produces metadata for every subject.
"""
import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Any

from pipeline.config import (
    DATA_DIR,
    CLASS_11_DIR,
    CLASS_12_DIR,
    SUBJECT_CODE_CATALOG
)

class SubjectExtractor:
    def __init__(self, logger=None):
        self.logger = logger
        self.manifest_file = DATA_DIR / "ACQUISITION_MANIFEST.json"

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[SubjectExtractor] {msg}")

    def sanitize_folder_name(self, code: str, name: str) -> str:
        clean = re.sub(r'[^A-Za-z0-9_]+', '_', name).strip('_').upper()
        return f"SUBJ_{code}_{clean}"

    def build_inventories(self) -> Dict[str, Any]:
        if not self.manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found at {self.manifest_file}. Run discovery first.")

        with open(self.manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.log(f"Processing {len(manifest)} manifest items into Class 11 and 12 inventories...")

        # Structure by class and subject code
        class_11_subjects: Dict[str, Dict[str, Any]] = {}
        class_12_subjects: Dict[str, Dict[str, Any]] = {}

        for item in manifest:
            code = item["subject_code"]
            name = item["subject_name"]
            classes = item["classes"]
            group = item["group"]
            stream = item["stream"]

            for cls in classes:
                target_dict = class_11_subjects if cls == "11" else class_12_subjects
                target_dir = CLASS_11_DIR if cls == "11" else CLASS_12_DIR

                folder_name = self.sanitize_folder_name(code, name)

                if code not in target_dict:
                    target_dict[code] = {
                        "subject_code": code,
                        "subject_name": name,
                        "class": cls,
                        "group": group,
                        "stream": stream,
                        "directory_name": folder_name,
                        "directory_path": str((target_dir / folder_name).relative_to(DATA_DIR)).replace("\\", "/"),
                        "resources": {
                            "syllabus": [],
                            "textbooks": [],
                            "sample_question_papers": [],
                            "marking_schemes": [],
                            "reading_materials": [],
                            "practicals": []
                        },
                        "total_resources": 0,
                        "status": "initialized"
                    }

                res_type = item["resource_type"]
                res_bucket = "syllabus"
                if res_type == "textbook":
                    res_bucket = "textbooks"
                elif res_type == "sample_question_paper":
                    res_bucket = "sample_question_papers"
                elif res_type == "marking_scheme":
                    res_bucket = "marking_schemes"
                elif res_type == "reading_material":
                    res_bucket = "reading_materials"
                elif res_type == "practical":
                    res_bucket = "practicals"

                target_dict[code]["resources"][res_bucket].append({
                    "title": item["title"],
                    "url": item["url"],
                    "session": item["session"],
                    "source": item["source"],
                    "license": item["license"]
                })
                target_dict[code]["total_resources"] += 1

        self.log(f"Identified {len(class_11_subjects)} distinct subjects for Class 11")
        self.log(f"Identified {len(class_12_subjects)} distinct subjects for Class 12")

        # Create folder hierarchies and per-subject metadata
        for cls_name, subj_dict, base_dir in [("11", class_11_subjects, CLASS_11_DIR), ("12", class_12_subjects, CLASS_12_DIR)]:
            for code, data in subj_dict.items():
                s_dir = base_dir / data["directory_name"]
                for subfolder in ["syllabus", "textbooks", "chapters", "notes", "question_papers", "solutions", "practicals"]:
                    (s_dir / subfolder).mkdir(parents=True, exist_ok=True)

                meta_path = s_dir / "metadata.json"
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            # Write SUBJECT_INVENTORY.json
            inv_json = base_dir / "SUBJECT_INVENTORY.json"
            inv_list = sorted(subj_dict.values(), key=lambda x: (x["group"], x["subject_code"], x["subject_name"]))
            with open(inv_json, "w", encoding="utf-8") as f:
                json.dump(inv_list, f, indent=2, ensure_ascii=False)

            # Write SUBJECT_INVENTORY.csv
            inv_csv = base_dir / "SUBJECT_INVENTORY.csv"
            with open(inv_csv, "w", encoding="utf-8", newline="") as f:
                fieldnames = ["subject_code", "subject_name", "class", "group", "stream", "total_resources", "directory_name", "status"]
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for s in inv_list:
                    writer.writerow(s)

            self.log(f"Saved Class {cls_name} inventory ({len(inv_list)} subjects) to {inv_json} and {inv_csv}")

        return {
            "class_11_count": len(class_11_subjects),
            "class_12_count": len(class_12_subjects)
        }

if __name__ == "__main__":
    extractor = SubjectExtractor()
    stats = extractor.build_inventories()
    print("Scaffold stats:", stats)
