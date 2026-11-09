"""
Text Extractor Module.
Extracts structured text from CBSE syllabus, SQP, and learning material PDFs using PyMuPDF.
Includes OCR fallback for scanned pages and parses units, chapters, marks, and competencies.
"""
import pymupdf
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class TextExtractor:
    def __init__(self, logger=None):
        self.logger = logger
        self._ocr_engine = None

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[TextExtractor] {msg}")

    def _get_ocr_engine(self):
        if self._ocr_engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._ocr_engine = RapidOCR()
            except Exception as e:
                self.log(f"OCR engine could not be initialized: {e}")
        return self._ocr_engine

    def clean_text(self, text: str) -> str:
        """Cleans encoding artifacts, non-standard hyphens, and whitespace anomalies."""
        # Normalize various unicode dashes
        text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufffd]', '-', text)
        text = text.replace('\r', '\n').replace('\t', ' ')
        text = re.sub(r'[ ]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_pdf_pages(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extracts text page by page with OCR fallback if selectable text is sparse."""
        pages_data = []
        doc = pymupdf.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            used_ocr = False
            
            # If page text is very short (< 40 chars), attempt OCR
            if len(text.strip()) < 40:
                engine = self._get_ocr_engine()
                if engine:
                    try:
                        pix = page.get_pixmap(dpi=150)
                        img_bytes = pix.tobytes("png")
                        ocr_result, _ = engine(img_bytes)
                        if ocr_result:
                            text = "\n".join([line[1] for line in ocr_result])
                            used_ocr = True
                    except Exception as e:
                        self.log(f"OCR failed on page {page_num+1} of {pdf_path.name}: {e}")

            cleaned = self.clean_text(text)
            pages_data.append({
                "page_number": page_num + 1,
                "text": cleaned,
                "used_ocr": used_ocr,
                "char_count": len(cleaned)
            })
        return pages_data

    def partition_senior_secondary(self, pages_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Partitions a Senior Secondary syllabus into Class XI and Class XII segments.
        CBSE Senior Secondary syllabi typically have Class XI first, followed by Class XII.
        """
        class_11_pages = []
        class_12_pages = []
        current_class = "11"

        for p in pages_data:
            txt = p["text"]
            
            # Detect transition to Class XII
            # Avoid matching header "CLASSES XI-XII"
            if re.search(r'COURSE\s+STRUCTURE\s*\n\s*CLASS\s*[-–—]?\s*XII', txt, re.IGNORECASE) or \
               re.search(r'\bCLASS\s*[-–—]?\s*XII\s*\(\d{4}', txt, re.IGNORECASE):
                current_class = "12"

            if current_class == "11":
                class_11_pages.append(p)
            else:
                class_12_pages.append(p)

        # Fallback if partition was not found
        if not class_12_pages:
            all_text = " ".join([p["text"].upper() for p in pages_data])
            if "CLASS - XII" in all_text or "CLASS XII" in all_text:
                for idx, p in enumerate(pages_data):
                    if re.search(r'CLASS\s*[-–—]?\s*XII', p["text"], re.IGNORECASE) and not re.search(r'CLASSES\s*XI', p["text"], re.IGNORECASE):
                        class_11_pages = pages_data[:idx]
                        class_12_pages = pages_data[idx:]
                        break

        if not class_12_pages:
            if "CLASS XII" in all_text and "CLASS XI" not in all_text:
                return {"11": [], "12": pages_data}
            return {"11": pages_data, "12": []}
            
        return {"11": class_11_pages, "12": class_12_pages}

    def parse_curriculum_structure(self, pages: List[Dict[str, Any]], target_class: str) -> Dict[str, Any]:
        """Parses units, chapters, marks, and assessment structure from pages."""
        combined_text = "\n".join([p["text"] for p in pages])
        
        # Extract assessment marks
        theory_marks = 80
        m_marks = re.search(r'Max(?:imum)?\.?\s*Marks[:\s]+(\d{2,3})', combined_text, re.IGNORECASE)
        if m_marks:
            theory_marks = int(m_marks.group(1))

        ia_marks = 100 - theory_marks if theory_marks <= 100 else 20

        # Extract Units: Match patterns like "Unit-I: Sets and Functions" or "Unit I: Sets"
        units = []
        unit_matches = re.finditer(r'(?:Unit[- ]*([IVXLCDM\d]+)[\s:]+([^\n]+))', combined_text, re.IGNORECASE)
        for m in unit_matches:
            unit_id = m.group(1).strip()
            unit_title = m.group(2).strip()
            if len(unit_title) > 2 and not any(u["title"] == unit_title for u in units):
                units.append({
                    "unit_id": f"Unit-{unit_id}",
                    "title": unit_title,
                    "topics": []
                })

        # Also check Course Structure table format: "I. \n Relations and Functions \n 08"
        if not units:
            table_units = re.finditer(r'([IVXLCDM]+)\.\s*\n\s*([A-Za-z\s,\-–]+)\n\s*(\d{1,2})', combined_text)
            for m in table_units:
                u_id = m.group(1)
                u_title = m.group(2).strip()
                u_marks = int(m.group(3))
                if len(u_title) > 3 and not any(u["title"] == u_title for u in units):
                    units.append({
                        "unit_id": f"Unit-{u_id}",
                        "title": u_title,
                        "marks": u_marks
                    })

        # Extract Chapters / Numbered Sections
        chapters = []
        chap_matches = re.finditer(r'(?:(?:^|\n)\s*(\d{1,2})\.\s+([A-Za-z][^\n]{3,60}))', combined_text)
        for m in chap_matches:
            chap_num = int(m.group(1))
            chap_title = m.group(2).strip()
            if chap_title and not any(c["title"] == chap_title for c in chapters):
                # Filter common table headers
                if not any(header in chap_title.upper() for header in ["QUESTION PAPER", "MAX. MARKS", "INTERNAL ASSESSMENT"]):
                    chapters.append({
                        "chapter_number": chap_num,
                        "title": chap_title
                    })

        return {
            "target_class": target_class,
            "theory_marks": theory_marks,
            "internal_assessment_marks": ia_marks,
            "total_marks": 100,
            "units_count": len(units),
            "units": units,
            "chapters_count": len(chapters),
            "chapters": chapters,
            "total_pages": len(pages),
            "full_text": combined_text
        }

if __name__ == "__main__":
    ext = TextExtractor()
    test_pdf = Path(r"D:\CBSE DATA SCRAPE\temp_raw_cache\Maths_SrSec_2025-26.pdf")
    if test_pdf.exists():
        pages = ext.extract_pdf_pages(test_pdf)
        split = ext.partition_senior_secondary(pages)
        print(f"Total pages: {len(pages)}")
        print(f"Class 11 pages: {len(split['11'])}, Class 12 pages: {len(split['12'])}")
        c11 = ext.parse_curriculum_structure(split['11'], "11")
        c12 = ext.parse_curriculum_structure(split['12'], "12")
        print("Class 11 parsed units:", len(c11["units"]), "chapters:", len(c11["chapters"]))
        print("Class 12 parsed units:", len(c12["units"]), "chapters:", len(c12["chapters"]))
        print("C11 Units:", [u["title"] for u in c11["units"]])
        print("C12 Units:", [u["title"] for u in c12["units"]])
