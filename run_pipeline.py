#!/usr/bin/env python3
"""
Root runner script for the Autonomous CBSE Class 11 & 12 Educational Data Acquisition System.
Can be executed with default settings or flags.
"""
import sys
import argparse
from pipeline.orchestrator import EducationalDataOrchestrator

def main():
    parser = argparse.ArgumentParser(description="CBSE Educational Data Acquisition Pipeline")
    parser.add_argument("--keep-cache", action="store_true", help="Do not delete temporary raw PDFs from ephemeral cache")
    args = parser.parse_args()

    clean_cache = not args.keep_cache
    orchestrator = EducationalDataOrchestrator(clean_cache_after_extraction=clean_cache)
    orchestrator.execute_complete_pipeline()

if __name__ == "__main__":
    main()
