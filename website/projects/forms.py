from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email

ACADEMIC_ROLES = [
    ("Lead Researcher", "Lead Researcher"),
    ("Co-Researcher", "Co-Researcher"),
    ("Faculty Guide", "Faculty Guide"),
    ("Research Assistant", "Research Assistant"),
    ("Literature Reviewer", "Literature Reviewer"),
    ("Member", "Member"),
]


class AddTaskForm(FlaskForm):
    name = StringField("Task Name", validators=[DataRequired()])
    description = TextAreaField("Task Description / Milestone Notes", validators=[DataRequired()])
    submit = SubmitField("Add Research Task")


class CreateProjectForm(FlaskForm):
    name = StringField("Research Project Title", validators=[DataRequired()])
    description = TextAreaField("Project Abstract / Objectives", validators=[DataRequired()])
    visibility = SelectField(
        "Visibility",
        choices=[("public", "Public (Open for Collaborator Discovery)"), ("private", "Private (Team Only)")],
        default="public",
        validators=[DataRequired()],
    )
    creator_id = HiddenField("Creator ID", default=None)
    submit = SubmitField("Create Research Project")

    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        if current_user.is_authenticated:
            self.creator_id.data = current_user.id


class ManageMembersForm(FlaskForm):
    email = StringField("Collaborator Email", validators=[DataRequired(), Email()])
    role = StringField("Academic Role")
    submit_add = SubmitField("Add Collaborator")
    submit_remove = SubmitField("Remove Collaborator")


class EditProjectForm(FlaskForm):
    name = StringField("Research Project Title", validators=[DataRequired()])
    description = TextAreaField("Project Abstract / Objectives")
    visibility = SelectField(
        "Visibility",
        choices=[("public", "Public (Open for Collaborator Discovery)"), ("private", "Private (Team Only)")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Project")


class AddProjectMemberForm(FlaskForm):
    email = StringField("Collaborator Email", validators=[DataRequired(), Email()])
    role = SelectField(
        "Academic Role",
        choices=ACADEMIC_ROLES,
        default="Co-Researcher",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add Collaborator")


class RemoveProjectMemberForm(FlaskForm):
    member_id = StringField("Member ID", validators=[DataRequired()])
    submit = SubmitField("Remove Collaborator")


class SendJoinRequestForm(FlaskForm):
    user_id = IntegerField("User ID")
    message = StringField("Collaboration Statement / Proposal", validators=[DataRequired()])
    role = SelectField(
        "Proposed Academic Role",
        choices=ACADEMIC_ROLES,
        default="Co-Researcher",
        validators=[DataRequired()],
    )
    sender_id = IntegerField("Sender ID")
    submit = SubmitField("Send Collaboration Request")


class AcceptRequestForm(FlaskForm):
    role = SelectField(
        "Assigned Academic Role",
        choices=ACADEMIC_ROLES,
        default="Co-Researcher",
        validators=[DataRequired()],
    )
    submit = SubmitField("Accept Collaborator")


class RejectRequestForm(FlaskForm):
    submit = SubmitField("Decline Request")


class InviteMemberForm(FlaskForm):
    email = StringField("Collaborator Email", validators=[DataRequired(), Email()])
    role = SelectField(
        "Academic Role",
        choices=ACADEMIC_ROLES,
        default="Co-Researcher",
        validators=[DataRequired()],
    )
    submit = SubmitField("Invite Collaborator")
