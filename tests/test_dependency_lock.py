"""Ensure reviewed Google Sheets sync dependencies are fully hash locked."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "requirements-sheet-sync.txt"
LOCK = ROOT / "requirements-sheet-sync.lock"


class DependencyLockTests(unittest.TestCase):
    def test_direct_dependencies_match_hash_lock(self):
        root = {}
        for line in SOURCE.read_text(encoding="utf-8").splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            name, version = text.split("==", 1)
            root[name] = version
        packages = {}
        current = None
        for line in LOCK.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            head = re.match(r"^([a-zA-Z0-9_.-]+)==([0-9][^\s\\]*)", stripped)
            if head:
                current = head.group(1)
                self.assertNotIn(current, packages)
                packages[current] = {"version": head.group(2), "hashes": []}
            for digest in re.findall(r"--hash=sha256:([0-9a-f]{64})", stripped):
                self.assertIsNotNone(current)
                packages[current]["hashes"].append(digest)
        self.assertGreaterEqual(len(packages), len(root))
        for name, version in root.items():
            self.assertIn(name, packages)
            self.assertEqual(packages[name]["version"], version)
        for name, record in packages.items():
            self.assertTrue(record["hashes"], f"Missing wheel hash: {name}")

    def test_lock_contains_no_unpinned_dependencies(self):
        for line in LOCK.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("--hash="):
                continue
            self.assertRegex(line, r"^[a-zA-Z0-9_.-]+==[0-9]")


if __name__ == "__main__":
    unittest.main()
