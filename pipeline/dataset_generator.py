"""
Dataset Generator Module.
Generates machine-readable educational datasets (Markdown, structured JSON, CSV, and AI training JSONL)
for each subject in Classes 11 and 12 from extracted syllabus and curriculum data.
"""
import json
import csv
from pathlib import Path
from typing import Dict, List, Any

class DatasetGenerator:
    def __init__(self, logger=None):
        self.logger = logger

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[DatasetGenerator] {msg}")

    def generate_subject_datasets(self, 
                                  subject_dir: Path, 
                                  subject_info: Dict[str, Any], 
                                  parsed_curriculum: Dict[str, Any],
                                  source_meta: Dict[str, Any]) -> Dict[str, str]:
        """
        Creates syllabus.md, curriculum_structure.json, curriculum_topics.csv,
        and ai_training_pairs.jsonl inside the designated subject directory.
        """
        cls = subject_info["class"]
        name = subject_info["subject_name"]
        code = subject_info["subject_code"]
        group = subject_info["group"]
        stream = subject_info["stream"]

        syllabus_dir = subject_dir / "syllabus"
        chapters_dir = subject_dir / "chapters"
        notes_dir = subject_dir / "notes"
        syllabus_dir.mkdir(parents=True, exist_ok=True)
        chapters_dir.mkdir(parents=True, exist_ok=True)
        notes_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate syllabus.md
        md_lines = [
            f"# CBSE Class {cls} {name} (Subject Code: {code})",
            f"**Stream / Group:** {stream} ({group})  ",
            f"**Academic Session:** {source_meta.get('session', '2025-26 / 2026-27')}  ",
            f"**Official Source:** [{source_meta.get('source', 'CBSE Academic Portal')}]({source_meta.get('url', '')})  ",
            f"**Document Checksum (SHA-256):** `{source_meta.get('sha256', 'N/A')}`  ",
            f"**Assessment Pattern:** {parsed_curriculum.get('theory_marks', 80)} Theory + {parsed_curriculum.get('internal_assessment_marks', 20)} Practical / Internal Assessment  ",
            "",
            "---",
            "",
            "## 1. Course Structure & Unit Breakdown",
            ""
        ]

        if parsed_curriculum.get("units"):
            md_lines.append("| Unit Number | Unit Title | Marks Allocation |")
            md_lines.append("|---|---|---|")
            for u in parsed_curriculum["units"]:
                u_id = u.get("unit_id", "Unit")
                u_title = u.get("title", "")
                u_marks = u.get("marks", "As per CBSE Distribution")
                md_lines.append(f"| **{u_id}** | {u_title} | {u_marks} |")
            md_lines.append("")

        if parsed_curriculum.get("chapters"):
            md_lines.append("## 2. Chapters & Key Topic Outlines")
            md_lines.append("")
            for c in parsed_curriculum["chapters"]:
                c_num = c.get("chapter_number", "")
                c_title = c.get("title", "")
                md_lines.append(f"- **Chapter {c_num}:** {c_title}")
            md_lines.append("")

        md_lines.append("## 3. Official Full Syllabus Transcript")
        md_lines.append("")
        md_lines.append("```text")
        full_text = parsed_curriculum.get("full_text", "")
        # truncate or include full text
        md_lines.append(full_text[:15000])
        if len(full_text) > 15000:
            md_lines.append("\n... [Full transcript continued in curriculum_structure.json] ...")
        md_lines.append("```")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("*Machine-readable dataset generated for educational AI model training and competency assessment.*")

        syllabus_md_path = syllabus_dir / "syllabus.md"
        with open(syllabus_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        # 2. Generate curriculum_structure.json
        struct_json = {
            "subject_name": name,
            "subject_code": code,
            "class": cls,
            "group": group,
            "stream": stream,
            "session": source_meta.get("session", "2025-26 / 2026-27"),
            "source_url": source_meta.get("url", ""),
            "sha256": source_meta.get("sha256", ""),
            "assessment": {
                "theory_marks": parsed_curriculum.get("theory_marks", 80),
                "internal_assessment_marks": parsed_curriculum.get("internal_assessment_marks", 20),
                "total_marks": 100
            },
            "units": parsed_curriculum.get("units", []),
            "chapters": parsed_curriculum.get("chapters", []),
            "full_text_excerpt": full_text[:20000]
        }
        struct_json_path = syllabus_dir / "curriculum_structure.json"
        with open(struct_json_path, "w", encoding="utf-8") as f:
            json.dump(struct_json, f, indent=2, ensure_ascii=False)

        # 3. Generate curriculum_topics.csv
        csv_path = syllabus_dir / "curriculum_topics.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["class", "subject_code", "subject_name", "item_type", "identifier", "title", "marks_allocation"])
            for u in parsed_curriculum.get("units", []):
                writer.writerow([cls, code, name, "Unit", u.get("unit_id", ""), u.get("title", ""), u.get("marks", "")])
            for c in parsed_curriculum.get("chapters", []):
                writer.writerow([cls, code, name, "Chapter", c.get("chapter_number", ""), c.get("title", ""), ""])

        # 4. Generate AI Training Pairs (JSONL)
        ai_pairs = []
        for u in parsed_curriculum.get("units", []):
            ai_pairs.append({
                "id": f"CBSE-{cls}-{code}-{u.get('unit_id', 'U')}-DEF",
                "class": cls,
                "subject": name,
                "subject_code": code,
                "unit": u.get("title"),
                "task_type": "curriculum_explanation",
                "instruction": f"Explain the pedagogical scope, core concepts, and assessment objectives for {u.get('title')} in CBSE Class {cls} {name}.",
                "expected_response": f"Under CBSE Class {cls} {name} ({code}), {u.get('unit_id')}: {u.get('title')} covers fundamental foundational principles aligned with NEP 2020 competency-based learning framework. Learners are evaluated on conceptual understanding, problem-solving application, and analytical rigor."
            })

        for c in parsed_curriculum.get("chapters", []):
            ai_pairs.append({
                "id": f"CBSE-{cls}-{code}-CH{c.get('chapter_number', '0')}-OUTLINE",
                "class": cls,
                "subject": name,
                "subject_code": code,
                "chapter": c.get("title"),
                "task_type": "step_by_step_marking_guide",
                "instruction": f"Generate a CBSE board-style step-by-step marking rubric and evaluation criteria for a problem based on {c.get('title')} in Class {cls} {name}.",
                "expected_response": f"CBSE Class {cls} {name} step-marking guide for {c.get('title')}: Step 1: Formula definition and axiomatic parameter assignment [1 Mark]. Step 2: Intermediate algebraic manipulation and justification of steps [1 Mark]. Step 3: Canonical solution formulation and unit checks [1 Mark]."
            })

        jsonl_path = notes_dir / "ai_training_pairs.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for pair in ai_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")

        return {
            "syllabus_md": str(syllabus_md_path),
            "structure_json": str(struct_json_path),
            "topics_csv": str(csv_path),
            "ai_training_jsonl": str(jsonl_path)
        }

if __name__ == "__main__":
    gen = DatasetGenerator()
    print("DatasetGenerator ready.")
