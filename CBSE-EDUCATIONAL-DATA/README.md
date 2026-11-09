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
|-- GLOBAL_DATASET_SPLITS/            # Unified CBSE Benchmark Splits (8,095 Pairs)
|   |-- train.jsonl                   # 80% Train Partition (6,410 Samples)
|   |-- val.jsonl                     # 10% Validation Partition (840 Samples)
|   |-- test.jsonl                    # 10% Evaluation Partition (845 Samples)
|   |-- train.csv / val.csv / test.csv# Tabular Split Formats
|   |-- SPLIT_REPORT.md               # Stratification and Split Distribution Report
|   |-- SPLIT_METRICS.json            # Machine-Readable Split Metrics
|
|-- CLASS_11/                         # Class 11 Senior Secondary Repository (114 Subjects)
|   |-- SUBJECT_INVENTORY.json        # Class 11 Complete Subject Catalog
|   |-- SUBJECT_INVENTORY.csv         # Tabular Stream & Group Index
|   |-- DATASET_SPLITS/               # Class 11 Consolidated Splits (train/val/test)
|   |-- SUBJ_041_MATHEMATICS/         # Subject Directory
|   |   |-- syllabus/                 # Markdown Syllabus, JSON Schema, Topics CSV & Splits
|   |   |-- textbooks/                # NCERT Official References & Bibliographies
|   |   |-- chapters/                 # Chapter-Wise Competency Mappings
|   |   |-- notes/                    # AI Training JSONL (Master, Train, Val, Test)
|   |   |-- question_papers/          # SQP Question Papers
|   |   |-- solutions/                # Official Marking Schemes
|   |   |-- practicals/               # Lab Manuals & Activity Guides
|   |   |-- metadata.json             # Subject Level Checksum & Status
|   |-- ...
|
|-- CLASS_12/                         # Class 12 Senior Secondary Repository (116 Subjects)
|   |-- SUBJECT_INVENTORY.json        # Class 12 Complete Subject Catalog
|   |-- SUBJECT_INVENTORY.csv         # Tabular Stream & Group Index
|   |-- DATASET_SPLITS/               # Class 12 Consolidated Splits (train/val/test)
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

## 4. Train / Validation / Test Benchmark Splits

To train and evaluate educational AI models, datasets are split at three distinct levels:

1. **Per-Subject Splits (`notes/` and `syllabus/`):**
   - `ai_training_train.jsonl` (80%), `ai_training_val.jsonl` (10%), `ai_training_test.jsonl` (10%)
   - `curriculum_train.csv` (80%), `curriculum_val.csv` (10%), `curriculum_test.csv` (10%)
   - `split_manifest.json` (deterministic split metadata and seed)

2. **Class-Level Consolidated Splits (`DATASET_SPLITS/`):**
   - `class_11_train.jsonl` (2,723 samples), `class_11_val.jsonl` (365 samples), `class_11_test.jsonl` (367 samples)
   - `class_12_train.jsonl` (3,687 samples), `class_12_val.jsonl` (475 samples), `class_12_test.jsonl` (478 samples)

3. **Global Unified Benchmark Splits (`GLOBAL_DATASET_SPLITS/`):**
   - `train.jsonl` (6,410 samples / 79.18%)
   - `val.jsonl` (840 samples / 10.38%)
   - `test.jsonl` (845 samples / 10.44%)
   - Total: 8,095 stratified instruction-tuning samples across Classes 11 & 12

### Loading into Python / HuggingFace `datasets`
```python
from datasets import load_dataset

# Load the global unified CBSE splits directly
cbse_data = load_dataset("json", data_files={
    "train": "CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/train.jsonl",
    "validation": "CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/val.jsonl",
    "test": "CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/test.jsonl"
})
print(cbse_data)
```

---

## 5. Re-Running the Automation

To execute or resume the pipeline:

```bash
# 1. Run the complete end-to-end pipeline (including splits and audit)
python run_pipeline.py

# 2. Run specific pipeline components
python -m pipeline.curriculum_discovery    # Re-discover all official resources
python -m pipeline.subject_extractor       # Re-build subject directories
python -m pipeline.data_splitter           # Re-generate train/val/test splits
python -m pipeline.auditor                 # Re-run QA and completeness audit
python -m pipeline.github_sync             # Sync commits to GitHub
```

---

## 6. Ephemeral Storage Compliance

In strict compliance with execution guidelines, large temporary PDF binaries are verified in ephemeral cache, hashed with SHA-256, parsed for structured educational text and metadata, and cleared from local disk to prevent storage bloat. All structured machine-readable knowledge is committed and preserved in the remote repository.
