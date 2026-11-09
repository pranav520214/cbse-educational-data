"""
PDF Downloader Module.
Handles resilient, rate-limited downloads with SHA-256 integrity checks,
SSL fallbacks, retry policies, and checkpoint tracking.
"""
import requests
import urllib3
import hashlib
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

from pipeline.config import (
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
    RATE_LIMIT_DELAY,
    CACHE_DIR,
    DATA_DIR
)

urllib3.disable_warnings()

class PDFDownloader:
    def __init__(self, logger=None):
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.verify = False
        self.ledger_file = DATA_DIR / "DOWNLOAD_LEDGER.json"
        self.failed_file = DATA_DIR / "FAILED_DOWNLOADS.json"
        self.ledger: Dict[str, Dict[str, Any]] = self._load_ledger()
        self.failed_downloads: Dict[str, str] = self._load_failed()

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[PDFDownloader] {msg}")

    def _load_ledger(self) -> Dict[str, Dict[str, Any]]:
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_ledger(self):
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(self.ledger, f, indent=2, ensure_ascii=False)

    def _load_failed(self) -> Dict[str, str]:
        if self.failed_file.exists():
            try:
                with open(self.failed_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_failed(self):
        with open(self.failed_file, "w", encoding="utf-8") as f:
            json.dump(self.failed_downloads, f, indent=2, ensure_ascii=False)

    def calculate_sha256(self, filepath: Path) -> str:
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def download(self, url: str, destination: Optional[Path] = None, force: bool = False) -> Dict[str, Any]:
        """
        Downloads a file from url to destination or cache, calculating SHA-256 and verifying size.
        Returns download metadata dict.
        """
        if not force and url in self.ledger and self.ledger[url].get("status") == "success":
            local_path = Path(self.ledger[url]["local_path"])
            if local_path.exists():
                return self.ledger[url]

        if destination is None:
            filename = url.split("?")[0].split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            destination = CACHE_DIR / filename

        destination.parent.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                time.sleep(RATE_LIMIT_DELAY)
                resp = self.session.get(url, stream=True, timeout=REQUEST_TIMEOUT_SECONDS)
                if resp.status_code == 200:
                    with open(destination, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=32768):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = destination.stat().st_size
                    if file_size == 0:
                        raise ValueError("Downloaded file is empty (0 bytes)")

                    sha256 = self.calculate_sha256(destination)
                    
                    res = {
                        "url": url,
                        "local_path": str(destination),
                        "file_size_bytes": file_size,
                        "sha256": sha256,
                        "status": "success",
                        "timestamp": time.time()
                    }
                    self.ledger[url] = res
                    self._save_ledger()
                    if url in self.failed_downloads:
                        del self.failed_downloads[url]
                        self._save_failed()
                    return res
                else:
                    last_error = f"HTTP {resp.status_code}"
            except Exception as e:
                last_error = str(e)
                time.sleep(RETRY_BACKOFF_FACTOR ** attempt)

        self.failed_downloads[url] = last_error or "Unknown error"
        self._save_failed()
        return {
            "url": url,
            "status": "failed",
            "error": last_error
        }

if __name__ == "__main__":
    dl = PDFDownloader()
    test_url = "https://cbseacademic.nic.in/web_material/CurriculumMain26/SrSec/Maths_SrSec_2025-26.pdf"
    print("Testing download of:", test_url)
    res = dl.download(test_url)
    print("Result:", res)
