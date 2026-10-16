from flask import url_for
from flask_testing import TestCase
from website import app, db
from website.accounts.models import User
from website.projects.models import Project, ProjectMember, Task
from website.documents.models import Document


class TestDashboard(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def setUp(self):
        self.user = User(
            email="test_lead@vit.ac.in",
            password="password123",
            is_confirmed=True,
        )
        self.collaborator = User(
            email="test_collab@vit.ac.in",
            password="password123",
            is_confirmed=True,
        )
        db.session.add(self.user)
        db.session.add(self.collaborator)
        db.session.commit()

        # Project 1: Lead by user
        self.p1 = Project(
            name="Autonomous Agent Reasoning Test",
            creator_id=self.user.id,
            description="Deep Learning multi-agent research",
            visibility="public",
        )
        # Project 2: Lead by collaborator, user is member
        self.p2 = Project(
            name="Neural Memory Indexing Test",
            creator_id=self.collaborator.id,
            description="Context management research",
            visibility="public",
        )
        db.session.add(self.p1)
        db.session.add(self.p2)
        db.session.commit()

        # Add memberships
        self.m1 = ProjectMember(user_id=self.user.id, project_id=self.p1.id, role="Lead Researcher")
        self.m2 = ProjectMember(user_id=self.user.id, project_id=self.p2.id, role="Co-Researcher")
        db.session.add(self.m1)
        db.session.add(self.m2)
        db.session.commit()

        # Add tasks
        self.t1 = Task(
            name="Literature Review Synthesis Test",
            description="Survey 50 recent arXiv papers",
            status="InProgress",
            role="Lead Researcher",
            project_id=self.p1.id,
        )
        self.t2 = Task(
            name="Benchmark Evaluation Test",
            description="Evaluate inference latency",
            status="Completed",
            role="Co-Researcher",
            project_id=self.p2.id,
        )
        db.session.add(self.t1)
        db.session.add(self.t2)
        db.session.commit()

        # Add document
        self.doc = Document(
            project_id=self.p1.id,
            uploaded_by=self.user.id,
            filename="test_arxiv_survey.pdf",
            file_path="/tmp/test_arxiv_survey.pdf",
            file_type="application/pdf",
            paper_title="Comprehensive Multi-Agent Survey Test",
            paper_authors="Dr. Alice, Dr. Bob",
            page_count=12,
            metadata_extracted=True,
        )
        db.session.add(self.doc)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        try:
            Document.query.filter(Document.filename.like('%test%')).delete(synchronize_session=False)
            Task.query.filter(Task.name.like('%Test%')).delete(synchronize_session=False)
            ProjectMember.query.filter(ProjectMember.id.in_([self.m1.id, self.m2.id])).delete(synchronize_session=False)
            Project.query.filter(Project.id.in_([self.p1.id, self.p2.id])).delete(synchronize_session=False)
            User.query.filter(User.id.in_([self.user.id, self.collaborator.id])).delete(synchronize_session=False)
            db.session.commit()
        except Exception:
            db.session.rollback()
        db.session.remove()

    def test_dashboard_unauthenticated_redirect(self):
        res = self.client.get(url_for("core.home"))
        self.assertStatus(res, 302)
        self.assertIn("/login", res.location)

    def test_dashboard_authenticated_aggregation(self):
        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_lead@vit.ac.in", "password": "password123"},
                follow_redirects=True,
            )

            res = self.client.get(url_for("core.home"))
            self.assert200(res)

            # Check that user projects are rendered
            self.assertIn(b"Autonomous Agent Reasoning Test", res.data)
            self.assertIn(b"Neural Memory Indexing Test", res.data)

            # Check tasks aggregation
            self.assertIn(b"Literature Review Synthesis Test", res.data)
            self.assertIn(b"Benchmark Evaluation Test", res.data)

# Document is tracked in metrics

            # Check portal metrics
            self.assertIn(b"Active Projects", res.data)
            self.assertIn(b"Research Papers", res.data)


if __name__ == "__main__":
    import unittest
    unittest.main()
