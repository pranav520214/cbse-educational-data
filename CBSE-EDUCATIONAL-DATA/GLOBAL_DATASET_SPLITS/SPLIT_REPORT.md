# CBSE Educational AI Dataset — Train / Validation / Test Benchmark Splits

**Total Samples:** 8,095 educational instruction-response pairs  
**Random Seed:** `42` (fully reproducible stratified split)  
**Stratification Keys:** Class (`11` vs `12`), CBSE Subject Code, Task Type  

---

## 1. Global Split Distribution

| Split | Sample Count | Percentage | Formats Available |
|---|---|---|---|
| **Train** | 6,410 | 79.18% | `train.jsonl`, `train.csv` |
| **Validation (Dev)** | 840 | 10.38% | `val.jsonl`, `val.csv` |
| **Test (Evaluation)** | 845 | 10.44% | `test.jsonl`, `test.csv` |
| **Total Unified** | **8,095** | **100.0%** | Comprehensive Benchmark |

---

## 2. Directory Layout & Partition Hierarchy

Splits are available at three granular levels:

1. **Subject-Level Splits:**
   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/notes/ai_training_train.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/notes/ai_training_val.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/notes/ai_training_test.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/syllabus/curriculum_train.csv`
   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/syllabus/curriculum_val.csv`
   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/syllabus/curriculum_test.csv`

2. **Class-Level Consolidated Splits:**
   - `CBSE-EDUCATIONAL-DATA/CLASS_11/DATASET_SPLITS/class_11_train.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_11/DATASET_SPLITS/class_11_val.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_11/DATASET_SPLITS/class_11_test.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_12/DATASET_SPLITS/class_12_train.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_12/DATASET_SPLITS/class_12_val.jsonl`
   - `CBSE-EDUCATIONAL-DATA/CLASS_12/DATASET_SPLITS/class_12_test.jsonl`

3. **Global Unified Benchmark Splits:**
   - `CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/train.jsonl`
   - `CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/val.jsonl`
   - `CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/test.jsonl`

---

## 3. Recommended Usage for AI Training & Evaluation

```python
from datasets import load_dataset

# Load the global unified CBSE train/val/test splits directly
dataset = load_dataset('json', data_files={
    'train': 'CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/train.jsonl',
    'validation': 'CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/val.jsonl',
    'test': 'CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/test.jsonl'
})
print(dataset)
```
