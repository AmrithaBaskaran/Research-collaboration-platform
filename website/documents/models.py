from datetime import datetime
from website import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)

    upload_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
    )

    # PyMuPDF Extracted Academic Metadata Fields
    paper_title = db.Column(db.String(500), nullable=True)
    paper_authors = db.Column(db.String(500), nullable=True)
    paper_abstract = db.Column(db.Text, nullable=True)
    paper_keywords = db.Column(db.String(500), nullable=True)
    paper_conclusions = db.Column(db.Text, nullable=True)
    paper_gaps = db.Column(db.Text, nullable=True)
    page_count = db.Column(db.Integer, nullable=True, default=1)
    creation_date = db.Column(db.String(100), nullable=True)
    metadata_extracted = db.Column(db.Boolean, default=False)

    project = db.relationship(
        "Project",
        backref=db.backref(
            "documents",
            cascade="all, delete-orphan",
        ),
    )

    uploader = db.relationship(
        "User",
        backref="uploaded_documents",
    )

    @property
    def is_pdf(self):
        return self.filename.lower().endswith(".pdf") or "pdf" in (self.file_type or "").lower()

    @property
    def display_title(self):
        return self.paper_title if (self.paper_title and self.paper_title != self.filename) else self.filename

    def __repr__(self):
        return f"<Document {self.filename}>"
