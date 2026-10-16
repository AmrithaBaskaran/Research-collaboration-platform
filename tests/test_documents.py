import io
import os
from flask import url_for
from flask_testing import TestCase
from website import app, db
from website.accounts.models import User
from website.projects.models import Project, ProjectMember
from website.documents.models import Document

try:
    import fitz
except ImportError:
    fitz = None


class TestDocuments(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def setUp(self):
        self.extra_user_ids = []
        self.user = User(
            email="test_docuser@example.com",
            password="password123",
            is_confirmed=True,
        )
        self.other_user = User(
            email="test_other@example.com",
            password="password123",
            is_confirmed=True,
        )
        db.session.add(self.user)
        db.session.add(self.other_user)
        db.session.commit()

        self.project = Project(
            name="Test Research AI Lab",
            creator_id=self.user.id,
            description="Paper test project",
            visibility="private",
        )
        db.session.add(self.project)
        db.session.commit()

        self.member = ProjectMember(
            user_id=self.user.id,
            project_id=self.project.id,
            role="creator",
        )
        db.session.add(self.member)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        try:
            Document.query.filter(Document.project_id == self.project.id).delete(synchronize_session=False)
            ProjectMember.query.filter(ProjectMember.project_id == self.project.id).delete(synchronize_session=False)
            Project.query.filter(Project.id == self.project.id).delete(synchronize_session=False)
            user_ids = [self.user.id, self.other_user.id]
            if hasattr(self, "extra_user_ids"):
                user_ids.extend(self.extra_user_ids)
            User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)
            db.session.commit()
        except Exception:
            db.session.rollback()
        db.session.remove()

    def test_document_model_properties(self):
        doc = Document(
            project_id=self.project.id,
            uploaded_by=self.user.id,
            filename="sample_paper.pdf",
            file_path="/tmp/sample_paper.pdf",
            file_type="application/pdf",
            paper_title="Advanced Neural Architectures",
            paper_authors="Dr. Smith",
            paper_abstract="Abstract content...",
            paper_keywords="AI, ML",
            paper_conclusions="Conclusion text",
            paper_gaps="Open problems",
            page_count=5,
            metadata_extracted=True,
        )
        db.session.add(doc)
        db.session.commit()

        self.assertTrue(doc.is_pdf)
        self.assertEqual(doc.display_title, "Advanced Neural Architectures")
        self.assertEqual(doc.page_count, 5)
        self.assertTrue(doc.metadata_extracted)

    def test_document_routes_unauthenticated(self):
        res = self.client.get(f"/projects/{self.project.id}/documents")
        self.assertStatus(res, 302)
        self.assertIn("/login", res.location)

    def test_document_routes_authenticated_member(self):
        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_docuser@example.com", "password": "password123"},
                follow_redirects=True,
            )

            res = self.client.get(f"/projects/{self.project.id}/documents")
            self.assert200(res)
            self.assertIn(b"Research Document Library", res.data)

            upload_res = self.client.get(f"/projects/{self.project.id}/documents/upload")
            self.assert200(upload_res)
            self.assertIn(b"Upload Document", upload_res.data)

    def test_pdf_upload_and_extraction_integration(self):
        if not fitz:
            return

        doc = fitz.open()
        page = doc.new_page()
        content = """Neural Context Management for Infinite LLMs
Dr. Alan Turing, Dr. Ada Lovelace

Abstract
We evaluate hierarchical memory tree indexing for long-running programming sessions.

Keywords: Context Management, Virtual Memory, Neural Networks

1. Introduction
Background on context rot in large language models...

2. Limitations and Research Gaps
Current context truncation discards crucial long-term project requirements.

3. Conclusions and Future Work
We demonstrated memory-based context optimization.
"""
        page.insert_text((50, 50), content)
        doc.set_metadata({
            "title": "Neural Context Management for Infinite LLMs",
            "author": "Dr. Alan Turing, Dr. Ada Lovelace",
            "keywords": "Context Management, Virtual Memory",
        })
        pdf_bytes = doc.write()
        doc.close()

        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_docuser@example.com", "password": "password123"},
                follow_redirects=True,
            )

            data = {
                "file": (io.BytesIO(pdf_bytes), "neural_context_paper.pdf"),
            }
            res = self.client.post(
                f"/projects/{self.project.id}/documents/upload",
                data=data,
                content_type="multipart/form-data",
                follow_redirects=True,
            )
            self.assert200(res)

            saved_doc = Document.query.filter_by(project_id=self.project.id).first()
            self.assertIsNotNone(saved_doc)
            self.assertEqual(saved_doc.paper_title, "Neural Context Management for Infinite LLMs")
            self.assertEqual(saved_doc.paper_authors, "Dr. Alan Turing, Dr. Ada Lovelace")
            self.assertTrue(saved_doc.metadata_extracted)
            self.assertIn("hierarchical memory tree indexing", saved_doc.paper_abstract)
            self.assertIn("Context Management", saved_doc.paper_keywords)
            self.assertIn("context truncation discards", saved_doc.paper_gaps)
            self.assertIn("demonstrated memory-based context optimization", saved_doc.paper_conclusions)

            details_res = self.client.get(f"/documents/{saved_doc.id}/details")
            self.assert200(details_res)
            self.assertIn(b"Neural Context Management for Infinite LLMs", details_res.data)
            self.assertIn(b"Dr. Alan Turing, Dr. Ada Lovelace", details_res.data)

            if os.path.exists(saved_doc.file_path):
                os.remove(saved_doc.file_path)

    def test_lead_researcher_can_delete_document(self):
        test_file_path = "/tmp/test_lead_delete.pdf"
        with open(test_file_path, "wb") as f:
            f.write(b"%PDF-1.4 test document content")

        doc = Document(
            project_id=self.project.id,
            uploaded_by=self.user.id,
            filename="lead_test_paper.pdf",
            file_path=test_file_path,
            file_type="application/pdf",
            paper_title="Lead Author Research",
        )
        db.session.add(doc)
        db.session.commit()

        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_docuser@example.com", "password": "password123"},
                follow_redirects=True,
            )

            # Check UI: delete button should be present in library and details
            list_res = self.client.get(f"/projects/{self.project.id}/documents")
            self.assert200(list_res)
            self.assertIn(f"/documents/{doc.id}/delete".encode(), list_res.data)

            details_res = self.client.get(f"/documents/{doc.id}/details")
            self.assert200(details_res)
            self.assertIn(f"/documents/{doc.id}/delete".encode(), details_res.data)

            # POST delete
            delete_res = self.client.post(
                f"/documents/{doc.id}/delete",
                follow_redirects=True,
            )
            self.assert200(delete_res)
            self.assertIn(b"Document deleted successfully.", delete_res.data)
            self.assertIsNone(Document.query.get(doc.id))
            self.assertFalse(os.path.exists(test_file_path))

    def test_co_researcher_can_delete_document(self):
        co_user = User(
            email="test_co_researcher@example.com",
            password="password123",
            is_confirmed=True,
        )
        db.session.add(co_user)
        db.session.commit()
        self.extra_user_ids.append(co_user.id)

        co_member = ProjectMember(
            user_id=co_user.id,
            project_id=self.project.id,
            role="Co-Researcher",
        )
        db.session.add(co_member)

        test_file_path = "/tmp/test_co_delete.pdf"
        with open(test_file_path, "wb") as f:
            f.write(b"%PDF-1.4 test document content")

        doc = Document(
            project_id=self.project.id,
            uploaded_by=self.user.id,
            filename="co_test_paper.pdf",
            file_path=test_file_path,
            file_type="application/pdf",
            paper_title="Co-Researcher Action",
        )
        db.session.add(doc)
        db.session.commit()

        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_co_researcher@example.com", "password": "password123"},
                follow_redirects=True,
            )

            # Check UI: delete button should be present in library and details
            list_res = self.client.get(f"/projects/{self.project.id}/documents")
            self.assert200(list_res)
            self.assertIn(f"/documents/{doc.id}/delete".encode(), list_res.data)

            details_res = self.client.get(f"/documents/{doc.id}/details")
            self.assert200(details_res)
            self.assertIn(f"/documents/{doc.id}/delete".encode(), details_res.data)

            # POST delete
            delete_res = self.client.post(
                f"/documents/{doc.id}/delete",
                follow_redirects=True,
            )
            self.assert200(delete_res)
            self.assertIn(b"Document deleted successfully.", delete_res.data)
            self.assertIsNone(Document.query.get(doc.id))
            self.assertFalse(os.path.exists(test_file_path))

    def test_other_member_and_non_member_cannot_delete_document(self):
        faculty_user = User(
            email="test_faculty_guide@example.com",
            password="password123",
            is_confirmed=True,
        )
        db.session.add(faculty_user)
        db.session.commit()
        self.extra_user_ids.append(faculty_user.id)

        faculty_member = ProjectMember(
            user_id=faculty_user.id,
            project_id=self.project.id,
            role="Faculty Guide",
        )
        db.session.add(faculty_member)

        test_file_path = "/tmp/test_faculty_doc.pdf"
        with open(test_file_path, "wb") as f:
            f.write(b"%PDF-1.4 test document content")

        doc = Document(
            project_id=self.project.id,
            uploaded_by=self.user.id,
            filename="faculty_test_paper.pdf",
            file_path=test_file_path,
            file_type="application/pdf",
            paper_title="Protected Document",
        )
        db.session.add(doc)
        db.session.commit()

        try:
            # 1. As Faculty Guide (Member but neither Lead Researcher nor Co-Researcher)
            with self.client:
                self.client.post(
                    url_for("accounts.login"),
                    data={"email": "test_faculty_guide@example.com", "password": "password123"},
                    follow_redirects=True,
                )

                # UI: delete button should NOT be present
                list_res = self.client.get(f"/projects/{self.project.id}/documents")
                self.assert200(list_res)
                self.assertNotIn(f"/documents/{doc.id}/delete".encode(), list_res.data)

                details_res = self.client.get(f"/documents/{doc.id}/details")
                self.assert200(details_res)
                self.assertNotIn(f"/documents/{doc.id}/delete".encode(), details_res.data)

                # POST delete should be rejected
                delete_res = self.client.post(
                    f"/documents/{doc.id}/delete",
                    follow_redirects=True,
                )
                self.assert200(delete_res)
                self.assertIn(b"Only the Lead Researcher and Co-Researcher can delete documents.", delete_res.data)
                self.assertIsNotNone(Document.query.get(doc.id))

            # 2. As Non-member (other_user)
            with self.client:
                self.client.post(
                    url_for("accounts.login"),
                    data={"email": "test_other@example.com", "password": "password123"},
                    follow_redirects=True,
                )

                delete_res = self.client.post(
                    f"/documents/{doc.id}/delete",
                    follow_redirects=True,
                )
                self.assert200(delete_res)
                self.assertIn(b"Only the Lead Researcher and Co-Researcher can delete documents.", delete_res.data)
                self.assertIsNotNone(Document.query.get(doc.id))

        finally:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)


if __name__ == "__main__":
    import unittest
    unittest.main()
