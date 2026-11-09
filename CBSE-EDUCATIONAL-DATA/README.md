# Autonomous CBSE Class 11 & 12 Educational Data Acquisition System

A production-grade, comprehensive educational dataset and curriculum repository covering **every subject, stream, unit, and chapter** for **CBSE Class 11 and Class 12**, prepared for educational AI training, RAG pipelines, and automated pedagogical evaluation.

---

## 1. System Architecture

```
CBSE-EDUCATIONAL-DATA/
|-- README.md                         # Repository Architecture and Guide
|-- LICENSES.md                       # Educational Fair Use & Government Open Data Licenses
|-- SOURCES.md                        # Master Source Catalog (CBSE & NCERT)
|-- DATASET_MANIFEST.json             # Unified Master Resource Manifest (560+ Items)
|-- COMPLETENESS_REPORT.md            # Automated Verification & Completeness Audit
|-- VERIFICATION_AUDIT.json           # Machine-Readable Completeness Metrics
|-- FAILED_DOWNLOADS.md               # Resilient Error Ledger & Retry Logs
|-- MISSING_RESOURCES.md              # Missing & Pending Input Catalog
|
|-- CLASS_11/                         # Class 11 Senior Secondary Repository (114 Subjects)
|   |-- SUBJECT_INVENTORY.json        # Class 11 Complete Subject Catalog
|   |-- SUBJECT_INVENTORY.csv         # Tabular Stream & Group Index
|   |-- SUBJ_041_MATHEMATICS/         # Subject Directory
|   |   |-- syllabus/                 # Markdown Syllabus, JSON Schema, Topics CSV
|   |   |-- textbooks/                # NCERT Official References & Bibliographies
|   |   |-- chapters/                 # Chapter-Wise Competency Mappings
|   |   |-- notes/                    # AI Training JSONL (Q&A / Rubrics)
|   |   |-- question_papers/          # SQP Question Papers
|   |   |-- solutions/                # Official Marking Schemes
|   |   |-- practicals/               # Lab Manuals & Activity Guides
|   |   |-- metadata.json             # Subject Level Checksum & Status
|   |-- ...
|
|-- CLASS_12/                         # Class 12 Senior Secondary Repository (116 Subjects)
|   |-- SUBJECT_INVENTORY.json        # Class 12 Complete Subject Catalog
|   |-- SUBJECT_INVENTORY.csv         # Tabular Stream & Group Index
|   |-- SUBJ_041_MATHEMATICS/         # Subject Directory
|   |-- ...
```

---

## 2. Curriculum Coverage

The dataset provides exhaustive coverage across all official CBSE curriculum groups:

1. **Group-A (Academic Electives):**
   - **Science Stream:** Mathematics (`041`), Applied Mathematics (`241`), Physics (`042`), Chemistry (`043`), Biology (`044`), Biotechnology (`045`)
   - **Commerce Stream:** Accountancy (`055`), Business Studies (`054`), Economics (`030`), Entrepreneurship (`066`)
   - **Humanities Stream:** History (`027`), Political Science (`028`), Geography (`029`), Psychology (`037`), Sociology (`039`), Legal Studies (`074`), Knowledge Traditions and Practices of India (`073`)
   - **Computing Stream:** Computer Science (`083`), Informatics Practices (`065`), Engineering Graphics (`046`)
   - **Visual & Performing Arts:** Fine Arts/Painting (`049`), Applied Arts (`052`), Dance (`056`), Music (`031`-`036`), Physical Education (`048`), NCC (`076`), Home Science (`064`)

2. **Group-L (Languages - 39 Languages):**
   - English Core (`301`), English Elective (`001`), Hindi Core (`302`), Hindi Elective (`002`), Sanskrit Core (`322`), Sanskrit Elective (`022`), Urdu Core/Elective, Assamese, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Arabic, French, German, Japanese, Russian, Spanish, etc.

3. **Group-S (Skill & Vocational Electives - 40+ Subjects):**
   - Artificial Intelligence (`843`), Data Science (`844`), Information Technology (`802`), Web Application (`803`), Financial Markets Management (`805`), Tourism (`806`), Retail (`801`), Healthcare (`813`), Yoga (`841`), Design Thinking (`848`), etc.

---

## 3. Machine-Readable Educational Formats

For each subject, the system generates structured artifacts optimized for training educational AI models:
- **`syllabus.md`**: Human and LLM-readable structured curriculum with units, chapters, marks distribution, and pedagogical guidelines.
- **`curriculum_structure.json`**: Strict JSON schema defining unit hierarchies, chapter allocations, theory vs practical marks.
- **`curriculum_topics.csv`**: Tabular dataset for relational queries, curriculum analytics, and knowledge graph mapping.
- **`ai_training_pairs.jsonl`**: Fine-tuning pairs for educational AI tutors, including curriculum explanations and official CBSE step-marking rubrics.

---

## 4. Re-Running the Automation

To execute or resume the pipeline:

```bash
# 1. Run the complete pipeline
python run_pipeline.py

# 2. Run specific pipeline components
python -m pipeline.curriculum_discovery    # Re-discover all official resources
python -m pipeline.subject_extractor       # Re-build subject directories
python -m pipeline.auditor                 # Re-run QA and completeness audit
python -m pipeline.github_sync             # Sync commits to GitHub
```

---

## 5. Ephemeral Storage Compliance

In strict compliance with execution guidelines, large temporary PDF binaries are verified in ephemeral cache, hashed with SHA-256, parsed for structured educational text and metadata, and cleared from local disk to prevent storage bloat. All structured machine-readable knowledge is committed and preserved in the remote repository.
