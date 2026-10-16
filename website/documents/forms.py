from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


class DocumentUploadForm(FlaskForm):
    file = FileField(
        "Document",
        validators=[
            FileRequired(),
            FileAllowed(
                ["pdf", "png", "jpg", "jpeg", "zip"],
                "Only PDF, PNG, JPG, JPEG, and ZIP files are allowed.",
            ),
        ],
    )

    submit = SubmitField("Upload Document")
