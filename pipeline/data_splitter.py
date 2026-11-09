"""
Data Splitter Module.
Creates reproducible, stratified Train / Validation / Test splits across:
1. Each individual subject's AI training pairs and curriculum topics.
2. Class 11 and Class 12 consolidated dataset splits.
3. Global unified benchmark dataset splits (8,000+ educational AI pairs).
"""
import json
import csv
import random
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from pipeline.config import (
    DATA_DIR,
    CLASS_11_DIR,
    CLASS_12_DIR
)

# Standard Split Ratios: 80% Train, 10% Validation, 10% Test
DEFAULT_TRAIN_RATIO = 0.80
DEFAULT_VAL_RATIO = 0.10
DEFAULT_TEST_RATIO = 0.10
DEFAULT_SEED = 42

class DataSplitter:
    def __init__(self, 
                 train_ratio: float = DEFAULT_TRAIN_RATIO, 
                 val_ratio: float = DEFAULT_VAL_RATIO, 
                 test_ratio: float = DEFAULT_TEST_RATIO, 
                 seed: int = DEFAULT_SEED,
                 logger=None):
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed
        self.logger = logger
        self.global_splits_dir = DATA_DIR / "GLOBAL_DATASET_SPLITS"
        self.global_splits_dir.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[DataSplitter] {msg}")

    def _partition_list(self, items: List[Any], rng: random.Random) -> Tuple[List[Any], List[Any], List[Any]]:
        """Splits a list into train, val, test with at least 1 item in test/val if possible."""
        n = len(items)
        if n == 0:
            return [], [], []
        if n == 1:
            return items, [], []
        if n == 2:
            return [items[0]], [], [items[1]]
        if n == 3:
            return [items[0]], [items[1]], [items[2]]

        shuffled = list(items)
        rng.shuffle(shuffled)

        n_val = max(1, round(n * self.val_ratio))
        n_test = max(1, round(n * self.test_ratio))
        # Ensure train gets at least 1 item
        if n_val + n_test >= n:
            n_val = 1
            n_test = 1
        n_train = n - n_val - n_test

        train = shuffled[:n_train]
        val = shuffled[n_train:n_train + n_val]
        test = shuffled[n_train + n_val:]
        return train, val, test

    def split_subject(self, subject_dir: Path) -> Dict[str, Any]:
        """Creates train/val/test splits for an individual subject directory."""
        notes_dir = subject_dir / "notes"
        syllabus_dir = subject_dir / "syllabus"
        meta_file = subject_dir / "metadata.json"

        # Deterministic per-subject seed
        subj_name = subject_dir.name
        subj_seed = self.seed + abs(hash(subj_name)) % 10000
        rng = random.Random(subj_seed)

        stats = {
            "subject_dir": str(subject_dir.relative_to(DATA_DIR)).replace("\\", "/"),
            "ai_pairs": {"train": 0, "val": 0, "test": 0, "total": 0},
            "topics": {"train": 0, "val": 0, "test": 0, "total": 0}
        }

        # 1. Split ai_training_pairs.jsonl
        ai_file = notes_dir / "ai_training_pairs.jsonl"
        if ai_file.exists():
            records = []
            with open(ai_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))

            if records:
                train_p, val_p, test_p = self._partition_list(records, rng)

                # Tag with split property
                for r in train_p: r["split"] = "train"
                for r in val_p: r["split"] = "val"
                for r in test_p: r["split"] = "test"

                # Write separate files
                for split_name, split_records in [("train", train_p), ("val", val_p), ("test", test_p)]:
                    out_path = notes_dir / f"ai_training_{split_name}.jsonl"
                    with open(out_path, "w", encoding="utf-8") as f:
                        for r in split_records:
                            f.write(json.dumps(r, ensure_ascii=False) + "\n")

                stats["ai_pairs"] = {
                    "train": len(train_p),
                    "val": len(val_p),
                    "test": len(test_p),
                    "total": len(records)
                }

        # 2. Split curriculum_topics.csv
        csv_file = syllabus_dir / "curriculum_topics.csv"
        if csv_file.exists():
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                rows = list(reader)

            if rows:
                t_train, t_val, t_test = self._partition_list(rows, rng)

                for split_name, split_rows in [("train", t_train), ("val", t_val), ("test", t_test)]:
                    out_csv = syllabus_dir / f"curriculum_{split_name}.csv"
                    fieldnames = list(headers)
                    if "split" not in fieldnames:
                        fieldnames.append("split")
                    with open(out_csv, "w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for r in split_rows:
                            r_copy = dict(r)
                            r_copy["split"] = split_name
                            writer.writerow(r_copy)

                stats["topics"] = {
                    "train": len(t_train),
                    "val": len(t_val),
                    "test": len(t_test),
                    "total": len(rows)
                }

        # Save subject split manifest
        split_manifest_path = notes_dir / "split_manifest.json"
        with open(split_manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "split_ratio": {"train": self.train_ratio, "val": self.val_ratio, "test": self.test_ratio},
                "seed": subj_seed,
                "metrics": stats
            }, f, indent=2)

        return stats

    def split_all_subjects_in_class(self, class_dir: Path, class_num: str) -> Dict[str, Any]:
        """Processes each subject folder in a class directory and produces class-level consolidated splits."""
        self.log(f"Splitting datasets for Class {class_num} subjects...")
        
        all_class_pairs = []
        all_class_topics = []
        subject_stats = []

        for s_dir in sorted(class_dir.iterdir()):
            if s_dir.is_dir() and s_dir.name.startswith("SUBJ_"):
                st = self.split_subject(s_dir)
                subject_stats.append(st)

                # Collect pairs for class-level consolidation
                ai_file = s_dir / "notes" / "ai_training_pairs.jsonl"
                if ai_file.exists():
                    with open(ai_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                all_class_pairs.append(json.loads(line.strip()))

                topics_file = s_dir / "syllabus" / "curriculum_topics.csv"
                if topics_file.exists():
                    with open(topics_file, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        all_class_topics.extend(list(reader))

        # Build Class-Level Consolidated Splits
        cls_splits_dir = class_dir / "DATASET_SPLITS"
        cls_splits_dir.mkdir(parents=True, exist_ok=True)

        rng = random.Random(self.seed + int(class_num))
        
        # Stratify by subject_code & task_type
        stratified_groups = defaultdict(list)
        for p in all_class_pairs:
            key = (p.get("subject_code", ""), p.get("task_type", ""))
            stratified_groups[key].append(p)

        c_train, c_val, c_test = [], [], []
        for key, group in stratified_groups.items():
            tr, va, te = self._partition_list(group, rng)
            for r in tr: r["split"] = "train"
            for r in va: r["split"] = "val"
            for r in te: r["split"] = "test"
            c_train.extend(tr)
            c_val.extend(va)
            c_test.extend(te)

        # Shuffle consolidated
        rng.shuffle(c_train)
        rng.shuffle(c_val)
        rng.shuffle(c_test)

        # Write Class consolidated JSONL
        for split_name, records in [("train", c_train), ("val", c_val), ("test", c_test)]:
            out_jsonl = cls_splits_dir / f"class_{class_num}_{split_name}.jsonl"
            with open(out_jsonl, "w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")

            out_csv = cls_splits_dir / f"class_{class_num}_{split_name}.csv"
            if records:
                keys = ["id", "class", "subject", "subject_code", "task_type", "instruction", "expected_response", "split"]
                with open(out_csv, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                    writer.writeheader()
                    for r in records:
                        writer.writerow(r)

        class_summary = {
            "class": class_num,
            "total_subjects": len(subject_stats),
            "total_ai_pairs": len(all_class_pairs),
            "split_counts": {
                "train": len(c_train),
                "val": len(c_val),
                "test": len(c_test)
            },
            "split_ratios": {
                "train_pct": round(len(c_train) / max(1, len(all_class_pairs)) * 100, 2),
                "val_pct": round(len(c_val) / max(1, len(all_class_pairs)) * 100, 2),
                "test_pct": round(len(c_test) / max(1, len(all_class_pairs)) * 100, 2)
            }
        }

        with open(cls_splits_dir / "SPLIT_METRICS.json", "w", encoding="utf-8") as f:
            json.dump(class_summary, f, indent=2)

        self.log(f"Class {class_num} split complete: {class_summary['split_counts']}")
        return class_summary

    def build_global_unified_splits(self) -> Dict[str, Any]:
        """Gathers all Class 11 and Class 12 pairs and creates a global benchmark split."""
        self.log("Assembling Global Unified CBSE Benchmark Dataset Splits...")

        all_pairs = []
        for cls_dir, cls_num in [(CLASS_11_DIR, "11"), (CLASS_12_DIR, "12")]:
            for s_dir in cls_dir.iterdir():
                if s_dir.is_dir() and s_dir.name.startswith("SUBJ_"):
                    ai_file = s_dir / "notes" / "ai_training_pairs.jsonl"
                    if ai_file.exists():
                        with open(ai_file, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.strip():
                                    all_pairs.append(json.loads(line.strip()))

        self.log(f"Loaded {len(all_pairs)} total AI training pairs across all subjects.")

        # Stratified partition by (class, subject_code, task_type)
        stratified = defaultdict(list)
        for p in all_pairs:
            key = (p.get("class", ""), p.get("subject_code", ""), p.get("task_type", ""))
            stratified[key].append(p)

        rng = random.Random(self.seed)
        g_train, g_val, g_test = [], [], []

        for key, group in stratified.items():
            tr, va, te = self._partition_list(group, rng)
            for r in tr: r["split"] = "train"
            for r in va: r["split"] = "val"
            for r in te: r["split"] = "test"
            g_train.extend(tr)
            g_val.extend(va)
            g_test.extend(te)

        rng.shuffle(g_train)
        rng.shuffle(g_val)
        rng.shuffle(g_test)

        # Write Global JSONL files
        for split_name, records in [("train", g_train), ("val", g_val), ("test", g_test)]:
            out_jsonl = self.global_splits_dir / f"{split_name}.jsonl"
            with open(out_jsonl, "w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")

            out_csv = self.global_splits_dir / f"{split_name}.csv"
            if records:
                keys = ["id", "class", "subject", "subject_code", "task_type", "instruction", "expected_response", "split"]
                with open(out_csv, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                    writer.writeheader()
                    for r in records:
                        writer.writerow(r)

        global_metrics = {
            "dataset_name": "CBSE Senior Secondary (Classes 11 & 12) Educational AI Benchmark",
            "seed": self.seed,
            "target_ratios": {"train": self.train_ratio, "val": self.val_ratio, "test": self.test_ratio},
            "total_samples": len(all_pairs),
            "split_samples": {
                "train": len(g_train),
                "val": len(g_val),
                "test": len(g_test)
            },
            "split_percentages": {
                "train": round(len(g_train) / max(1, len(all_pairs)) * 100, 2),
                "val": round(len(g_val) / max(1, len(all_pairs)) * 100, 2),
                "test": round(len(g_test) / max(1, len(all_pairs)) * 100, 2)
            },
            "stratification_factors": ["class", "subject_code", "task_type"]
        }

        # Save metrics JSON
        with open(self.global_splits_dir / "SPLIT_METRICS.json", "w", encoding="utf-8") as f:
            json.dump(global_metrics, f, indent=2)

        # Generate Markdown Report
        md_lines = [
            "# CBSE Educational AI Dataset — Train / Validation / Test Benchmark Splits",
            "",
            f"**Total Samples:** {len(all_pairs):,} educational instruction-response pairs  ",
            f"**Random Seed:** `{self.seed}` (fully reproducible stratified split)  ",
            f"**Stratification Keys:** Class (`11` vs `12`), CBSE Subject Code, Task Type  ",
            "",
            "---",
            "",
            "## 1. Global Split Distribution",
            "",
            "| Split | Sample Count | Percentage | Formats Available |",
            "|---|---|---|---|",
            f"| **Train** | {len(g_train):,} | {global_metrics['split_percentages']['train']}% | `train.jsonl`, `train.csv` |",
            f"| **Validation (Dev)** | {len(g_val):,} | {global_metrics['split_percentages']['val']}% | `val.jsonl`, `val.csv` |",
            f"| **Test (Evaluation)** | {len(g_test):,} | {global_metrics['split_percentages']['test']}% | `test.jsonl`, `test.csv` |",
            f"| **Total Unified** | **{len(all_pairs):,}** | **100.0%** | Comprehensive Benchmark |",
            "",
            "---",
            "",
            "## 2. Directory Layout & Partition Hierarchy",
            "",
            "Splits are available at three granular levels:",
            "",
            "1. **Subject-Level Splits:**",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/notes/ai_training_train.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/notes/ai_training_val.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/notes/ai_training_test.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/syllabus/curriculum_train.csv`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/syllabus/curriculum_val.csv`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_<XI/XII>/SUBJ_<CODE>_<NAME>/syllabus/curriculum_test.csv`",
            "",
            "2. **Class-Level Consolidated Splits:**",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_11/DATASET_SPLITS/class_11_train.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_11/DATASET_SPLITS/class_11_val.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_11/DATASET_SPLITS/class_11_test.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_12/DATASET_SPLITS/class_12_train.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_12/DATASET_SPLITS/class_12_val.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/CLASS_12/DATASET_SPLITS/class_12_test.jsonl`",
            "",
            "3. **Global Unified Benchmark Splits:**",
            "   - `CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/train.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/val.jsonl`",
            "   - `CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/test.jsonl`",
            "",
            "---",
            "",
            "## 3. Recommended Usage for AI Training & Evaluation",
            "",
            "```python",
            "from datasets import load_dataset",
            "",
            "# Load the global unified CBSE train/val/test splits directly",
            "dataset = load_dataset('json', data_files={",
            "    'train': 'CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/train.jsonl',",
            "    'validation': 'CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/val.jsonl',",
            "    'test': 'CBSE-EDUCATIONAL-DATA/GLOBAL_DATASET_SPLITS/test.jsonl'",
            "})",
            "print(dataset)",
            "```",
            ""
        ]

        with open(self.global_splits_dir / "SPLIT_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        self.log(f"Global Unified Splits complete: {global_metrics['split_samples']}")
        return global_metrics

    def run_all_splits(self) -> Dict[str, Any]:
        """Executes subject-level, class-level, and global unified splits."""
        self.log("Starting full data splitting pipeline...")
        c11_summary = self.split_all_subjects_in_class(CLASS_11_DIR, "11")
        c12_summary = self.split_all_subjects_in_class(CLASS_12_DIR, "12")
        global_summary = self.build_global_unified_splits()

        return {
            "class_11": c11_summary,
            "class_12": c12_summary,
            "global": global_summary
        }

if __name__ == "__main__":
    splitter = DataSplitter()
    res = splitter.run_all_splits()
    print("Split execution finished:", res["global"]["split_samples"])
