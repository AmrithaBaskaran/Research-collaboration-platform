import os
import unittest
from website.documents.extractor import (
    clean_text,
    extract_section_by_patterns,
    extract_pdf_metadata,
)

try:
    import fitz
except ImportError:
    fitz = None


class TestPdfExtractor(unittest.TestCase):
    def test_clean_text(self):
        sample = "Discov-\nery of novel    multi-agent   models.\n\n\nNext line."
        cleaned = clean_text(sample)
        self.assertIn("Discovery", cleaned)
        self.assertNotIn("Discov-\nery", cleaned)
        self.assertNotIn("    ", cleaned)

    def test_clean_text_with_max_length(self):
        sample = "This is a long sentence that should be cleanly truncated at a word boundary."
        cleaned = clean_text(sample, max_length=25)
        self.assertTrue(len(cleaned) <= 28)
        self.assertTrue(cleaned.endswith("..."))

    def test_extract_section_by_patterns(self):
        sample_text = """
        1. Abstract
        This research paper introduces autonomous collaboration tools for student research teams.
        
        2. Keywords
        Research, Collaboration, PyMuPDF
        """
        abstract = extract_section_by_patterns(
            sample_text,
            ["abstract"],
            ["keywords", "introduction"]
        )
        self.assertIn("autonomous collaboration tools", abstract)

    @unittest.skipIf(fitz is None, "PyMuPDF not installed")
    def test_extract_pdf_metadata_synthetic(self):
        # Create a test PDF in /tmp
        doc = fitz.open()
        page = doc.new_page()
        content = """Distributed Academic Research Coordination
Dr. Alice Walker, Prof. Robert Davis
Department of Computing

Abstract
We present a modern architecture for academic literature synthesis and task scheduling across distributed university faculties.

Keywords: Academic Systems, Distributed Computing, Literature Review

1. Introduction
Academic research is highly collaborative...

2. Limitations and Research Gaps
Existing single-server systems fail to preserve PDF metadata across multiple collaborative sessions.

3. Conclusions and Future Work
Our framework successfully integrates intelligent document parsing with role-based coordination.

References
[1] Walker et al., Academic Systems, 2026.
"""
        page.insert_text((50, 50), content)
        doc.set_metadata({
            "title": "Distributed Academic Research Coordination",
            "author": "Dr. Alice Walker, Prof. Robert Davis",
            "keywords": "Academic Systems, Distributed Computing",
        })
        test_pdf_path = "/tmp/test_synthetic_paper.pdf"
        doc.save(test_pdf_path)
        doc.close()

        result = extract_pdf_metadata(test_pdf_path)

        self.assertTrue(result["metadata_extracted"])
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(result["paper_title"], "Distributed Academic Research Coordination")
        self.assertEqual(result["paper_authors"], "Dr. Alice Walker, Prof. Robert Davis")
        self.assertIn("architecture for academic literature synthesis", result["paper_abstract"])
        self.assertIn("Academic Systems", result["paper_keywords"])
        self.assertIn("preserve PDF metadata", result["paper_gaps"])
        self.assertIn("successfully integrates intelligent document parsing", result["paper_conclusions"])

        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

    def test_extract_nonexistent_pdf(self):
        result = extract_pdf_metadata("/tmp/nonexistent_file_12345.pdf")
        self.assertFalse(result["metadata_extracted"])
        self.assertEqual(result["page_count"], 1)


if __name__ == "__main__":
    unittest.main()
