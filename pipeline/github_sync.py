"""
GitHub Synchronization Module.
Automates batch staging, committing, pushing, and remote API verification
for pranav520214/cbse-educational-data.
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List

from pipeline.config import ROOT_DIR, DATA_DIR

class GitHubSync:
    def __init__(self, repo_name: str = "pranav520214/cbse-educational-data", logger=None):
        self.repo_name = repo_name
        self.logger = logger
        self.root = ROOT_DIR

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[GitHubSync] {msg}")

    def run_cmd(self, cmd: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=str(self.root),
            capture_output=True,
            text=True,
            check=False
        )

    def commit_and_push(self, commit_message: str, stage_paths: List[str] = None) -> Dict[str, Any]:
        """Stages files, creates commit, and pushes to main branch."""
        if stage_paths:
            for p in stage_paths:
                self.run_cmd(["git", "add", p])
        else:
            self.run_cmd(["git", "add", "."])

        # Check status
        status = self.run_cmd(["git", "status", "--porcelain"])
        if not status.stdout.strip():
            self.log("No new changes to commit.")
            return {"status": "up_to_date", "message": "Nothing to commit"}

        commit_res = self.run_cmd(["git", "commit", "-m", commit_message])
        self.log(f"Committed: {commit_message}")

        # Push to remote
        push_res = self.run_cmd(["git", "push", "-u", "origin", "main"])
        if push_res.returncode != 0:
            self.log(f"Push warning/error: {push_res.stderr}")
            return {"status": "push_failed", "error": push_res.stderr}

        self.log("Successfully pushed to GitHub origin main.")
        return {"status": "success", "commit": commit_message}

    def verify_remote_presence(self) -> Dict[str, Any]:
        """Queries GitHub CLI API to verify remote commits and branch status."""
        self.log(f"Verifying remote repository status for {self.repo_name}...")
        api_res = self.run_cmd(["gh", "api", f"repos/{self.repo_name}/commits"])
        if api_res.returncode == 0:
            try:
                commits = json.loads(api_res.stdout)
                latest_sha = commits[0]["sha"] if commits else "None"
                latest_msg = commits[0]["commit"]["message"] if commits else "None"
                self.log(f"Remote verified! Latest commit: {latest_sha[:8]} - {latest_msg}")
                return {
                    "verified": True,
                    "latest_sha": latest_sha,
                    "latest_message": latest_msg,
                    "total_remote_commits": len(commits)
                }
            except Exception as e:
                self.log(f"Error parsing commits: {e}")
        return {"verified": False, "error": api_res.stderr}

if __name__ == "__main__":
    sync = GitHubSync()
    ver = sync.verify_remote_presence()
    print("Remote verification:", ver)
