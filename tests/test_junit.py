import tempfile
import unittest
from pathlib import Path

from agent_evidence.core import InvalidTrace
from agent_evidence.junit import summarize_junit, MAX_JUNIT_BYTES


class JUnitArtifactTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.file = Path(tmp.name) / "results.xml"

    def parse(self, content):
        self.file.write_text(content, encoding="utf-8")
        return summarize_junit(self.file)

    def test_all_passing(self):
        x = self.parse('<testsuite><testcase name="a"/><testcase name="b"/></testsuite>')
        self.assertTrue(x["all_testcases_pass"])
        self.assertEqual(x["testcases"], 2)
        self.assertFalse(x["provenance_verified"])

    def test_failed_case(self):
        x = self.parse('<testsuite><testcase name="a"><failure/></testcase></testsuite>')
        self.assertFalse(x["all_testcases_pass"])
        self.assertEqual(x["failed"], 1)

    def test_error_case(self):
        x = self.parse('<testsuite><testcase name="a"><error/></testcase></testsuite>')
        self.assertEqual(x["errors"], 1)

    def test_skipped_case(self):
        x = self.parse('<testsuite><testcase name="a"><skipped/></testcase></testsuite>')
        self.assertEqual(x["skipped"], 1)
        self.assertFalse(x["all_testcases_pass"])

    def test_nested_suites(self):
        x = self.parse('<testsuites><testsuite><testcase name="a"/></testsuite><testsuite><testcase name="b"/></testsuite></testsuites>')
        self.assertEqual(x["testcases"], 2)

    def test_empty_suite_is_not_pass(self):
        x = self.parse('<testsuite tests="0"/>')
        self.assertFalse(x["all_testcases_pass"])

    def test_root_rejected(self):
        with self.assertRaises(InvalidTrace):
            self.parse('<foo><testcase name="a"/></foo>')

    def test_missing_name_rejected(self):
        with self.assertRaises(InvalidTrace):
            self.parse('<testsuite><testcase/></testsuite>')

    def test_invalid_xml_rejected(self):
        with self.assertRaises(InvalidTrace):
            self.parse('<testsuite>')

    def test_xml_too_large_rejected(self):
        self.file.write_bytes(b"x" * (MAX_JUNIT_BYTES + 1))
        with self.assertRaises(InvalidTrace):
            summarize_junit(self.file)

    def test_doctype_is_rejected(self):
        with self.assertRaises(InvalidTrace):
            self.parse('<!DOCTYPE foo [<!ENTITY bad "expanded">]><testsuite/>')

    def test_external_entity_is_rejected(self):
        with self.assertRaises(InvalidTrace):
            self.parse('<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><testsuite/>')

    def test_missing_file_rejected(self):
        with self.assertRaises(InvalidTrace):
            summarize_junit(self.file)


if __name__ == "__main__":
    unittest.main()
