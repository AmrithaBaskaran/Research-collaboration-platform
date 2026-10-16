from unittest import mock
from flask import url_for
from flask_testing import TestCase
from website import app, db
from website.accounts.models import User, Profile
from website.accounts.forms import RegisterForm, LoginForm, ProfileForm


class TestLogin(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def test_login_route_get(self):
        response = self.client.get(url_for("accounts.login"))
        self.assert200(response)

    def test_login_route_post(self):
        data = {"email": "test@example.com", "password": "password"}

        with mock.patch("website.accounts.models.User.query") as mock_query:
            mock_query.filter_by.return_value.first.return_value = None

            with self.client:
                response = self.client.post(
                    url_for("accounts.login"), data=data, follow_redirects=True
                )
                self.assert200(response)


from website.projects.models import Project, ProjectMember, Task, Comment

class TestTaskDiscussion(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def setUp(self):
        self.user = User(email="test_discussion_user@vit.ac.in", password="password123", is_confirmed=True)
        db.session.add(self.user)
        db.session.commit()

        # Profile with photo = None
        self.profile = Profile(user_id=self.user.id, full_name="Test Discussion User", age=25, bio="Test Bio", photo=None)
        db.session.add(self.profile)

        self.project = Project(name="Discussion Test Project", creator_id=self.user.id, description="Testing discussions", visibility="public")
        db.session.add(self.project)
        db.session.commit()

        self.member = ProjectMember(user_id=self.user.id, project_id=self.project.id, role="Lead Researcher")
        db.session.add(self.member)

        self.task = Task(name="Discussion Test Task", description="Testing discussion comment rendering", status="InProgress", role="Lead Researcher", project_id=self.project.id)
        db.session.add(self.task)
        db.session.commit()

        self.comment = Comment(text="Hello research team this is a test comment", user_id=self.user.id, task_id=self.task.id)
        db.session.add(self.comment)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        try:
            Comment.query.filter_by(id=self.comment.id).delete(synchronize_session=False)
            Task.query.filter_by(id=self.task.id).delete(synchronize_session=False)
            ProjectMember.query.filter_by(id=self.member.id).delete(synchronize_session=False)
            Project.query.filter_by(id=self.project.id).delete(synchronize_session=False)
            Profile.query.filter_by(id=self.profile.id).delete(synchronize_session=False)
            User.query.filter_by(id=self.user.id).delete(synchronize_session=False)
            db.session.commit()
        except Exception:
            db.session.rollback()
        db.session.remove()

    def test_view_task_details_with_null_photo(self):
        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_discussion_user@vit.ac.in", "password": "password123"},
                follow_redirects=True,
            )
            res = self.client.get(
                url_for("projects.view_task_details", project_id=self.project.id, task_id=self.task.id)
            )
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Discussion: Discussion Test Task", res.data)
            self.assertIn(b"Hello research team this is a test comment", res.data)
            self.assertIn(b"Test Discussion User", res.data)

    def test_delete_task_authorized(self):
        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_discussion_user@vit.ac.in", "password": "password123"},
                follow_redirects=True,
            )
            # Create a dedicated task to delete
            task_to_delete = Task(name="Task To Delete", description="Desc", status="Pending", role="Co-Researcher", project_id=self.project.id)
            db.session.add(task_to_delete)
            db.session.commit()
            task_id = task_to_delete.id

            res = self.client.post(url_for("tasks.delete_task", task_id=task_id), follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"deleted successfully", res.data)
            self.assertIsNone(Task.query.get(task_id))


class TestPublicProjects(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def setUp(self):
        self.user = User(email="test_pub_user@example.com", password="password123", is_confirmed=True)
        self.other_user = User(email="test_pub_other@example.com", password="password123", is_confirmed=True)
        db.session.add(self.user)
        db.session.add(self.other_user)
        db.session.commit()

        # 1. Public project created by self.user
        self.p_own = Project(name="User Own Public Project", creator_id=self.user.id, description="Owned by user", visibility="public")
        # 2. Public project created by other_user, where self.user is a collaborator
        self.p_collab = Project(name="Collaborator Public Project", creator_id=self.other_user.id, description="Collab project", visibility="public")
        # 3. Public project created by other_user, where self.user is NOT involved
        self.p_open = Project(name="Open Discoverable Project", creator_id=self.other_user.id, description="Open to join", visibility="public")
        # 4. Private project by other_user
        self.p_private = Project(name="Private Other Project", creator_id=self.other_user.id, description="Private project", visibility="private")

        db.session.add_all([self.p_own, self.p_collab, self.p_open, self.p_private])
        db.session.commit()

        # Add self.user as member of p_collab
        self.member_collab = ProjectMember(user_id=self.user.id, project_id=self.p_collab.id, role="Co-Researcher")
        db.session.add(self.member_collab)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        try:
            ProjectMember.query.filter_by(id=self.member_collab.id).delete(synchronize_session=False)
            Project.query.filter(Project.id.in_([self.p_own.id, self.p_collab.id, self.p_open.id, self.p_private.id])).delete(synchronize_session=False)
            User.query.filter(User.id.in_([self.user.id, self.other_user.id])).delete(synchronize_session=False)
            db.session.commit()
        except Exception:
            db.session.rollback()
        db.session.remove()

    def test_public_projects_excludes_joined_and_created_projects_when_authenticated(self):
        with self.client:
            self.client.post(
                url_for("accounts.login"),
                data={"email": "test_pub_user@example.com", "password": "password123"},
                follow_redirects=True,
            )

            res = self.client.get(url_for("projects.public_projects"))
            self.assertEqual(res.status_code, 200)

            # Must show the open project that the user is NOT part of
            self.assertIn(b"Open Discoverable Project", res.data)

            # Must NOT show projects the user created
            self.assertNotIn(b"User Own Public Project", res.data)

            # Must NOT show projects the user is a member of
            self.assertNotIn(b"Collaborator Public Project", res.data)

            # Must NOT show private projects
            self.assertNotIn(b"Private Other Project", res.data)

    def test_public_projects_shows_all_public_projects_when_unauthenticated(self):
        res = self.client.get(url_for("projects.public_projects"))
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Open Discoverable Project", res.data)
        self.assertIn(b"User Own Public Project", res.data)
        self.assertIn(b"Collaborator Public Project", res.data)
        self.assertNotIn(b"Private Other Project", res.data)
