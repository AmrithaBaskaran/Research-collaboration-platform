from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

TASK_ACADEMIC_ROLES = [
    ("Lead Researcher", "Lead Researcher"),
    ("Co-Researcher", "Co-Researcher"),
    ("Faculty Guide", "Faculty Guide"),
    ("Research Assistant", "Research Assistant"),
    ("Literature Review", "Literature Review"),
    ("Methodology & Experiments", "Methodology & Experiments"),
    ("Data Analysis", "Data Analysis"),
    ("Paper Writing & Publication", "Paper Writing & Publication"),
    ("Member", "General Team Member"),
]


class TaskForm(FlaskForm):
    name = StringField("Task Name / Milestone", validators=[DataRequired()])
    description = TextAreaField("Task Details & Instructions")
    status = SelectField(
        "Status",
        choices=[
            ("Pending", "To Do"),
            ("InProgress", "In Progress"),
            ("Completed", "Completed"),
            ("Overdue", "Overdue"),
        ],
        default="Pending",
    )
    role = SelectField(
        "Assigned Role / Functional Area",
        choices=TASK_ACADEMIC_ROLES,
        default="Co-Researcher",
        validators=[DataRequired()],
    )


class CommentForm(FlaskForm):
    text = TextAreaField("Discussion Comment / Update", validators=[DataRequired()])
    submit = SubmitField("Post Comment")


class HiddenForm(FlaskForm):
    pass
