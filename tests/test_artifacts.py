import hashlib
import tempfile
import unittest
from pathlib import Path

from agent_evidence.artifacts import verify_manifest
from agent_evidence.core import InvalidTrace


class ArtifactIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sample = self.root / "result.txt"
        self.sample.write_bytes(b"example output\n")
        self.digest = hashlib.sha256(self.sample.read_bytes()).hexdigest()

    def manifest(self):
        return {"artifacts": [{"path": "result.txt", "sha256": self.digest, "size": 15}]}

    def test_matching_bytes(self):
        self.assertTrue(verify_manifest(self.root, self.manifest())["all_artifacts_match"])

    def test_tampered_bytes(self):
        self.sample.write_bytes(b"example other output\n")
        self.assertFalse(verify_manifest(self.root, self.manifest())["all_artifacts_match"])

    def test_missing_file(self):
        self.sample.unlink()
        self.assertEqual(verify_manifest(self.root, self.manifest())["results"][0]["issue"],
                         "missing_or_not_regular_file")

    def test_empty_manifest_is_not_supported(self):
        self.assertFalse(verify_manifest(self.root, {"artifacts": []})["all_artifacts_match"])

    def test_path_traversal_rejected(self):
        data = self.manifest()
        data["artifacts"][0]["path"] = "../result.txt"
        with self.assertRaises(InvalidTrace):
            verify_manifest(self.root, data)

    def test_absolute_path_rejected(self):
        data = self.manifest()
        data["artifacts"][0]["path"] = str(self.sample)
        with self.assertRaises(InvalidTrace):
            verify_manifest(self.root, data)

    def test_duplicate_files_rejected(self):
        data = self.manifest()
        data["artifacts"] *= 2
        with self.assertRaises(InvalidTrace):
            verify_manifest(self.root, data)

    def test_symlink_rejected(self):
        (self.root / "link.txt").symlink_to(self.sample)
        data = self.manifest()
        data["artifacts"][0]["path"] = "link.txt"
        with self.assertRaises(InvalidTrace):
            verify_manifest(self.root, data)

    def test_boolean_size_rejected(self):
        data = self.manifest()
        data["artifacts"][0]["size"] = True
        with self.assertRaises(InvalidTrace):
            verify_manifest(self.root, data)

    def test_invalid_digest_rejected(self):
        data = self.manifest()
        data["artifacts"][0]["sha256"] = "not-a-sha256"
        with self.assertRaises(InvalidTrace):
            verify_manifest(self.root, data)


if __name__ == "__main__":
    unittest.main()
