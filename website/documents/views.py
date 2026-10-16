import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from website import db
from website.documents.extractor import extract_pdf_metadata
from website.documents.forms import DocumentUploadForm
from website.documents.models import Document
from website.projects.models import Project, ProjectMember


documents_bp = Blueprint("documents", __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "zip"}


def is_project_member(project, user=None):
    if user is None:
        user = current_user
    if not user.is_authenticated:
        return False
    if project.creator_id == user.id:
        return True

    member = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=user.id,
    ).first()

    return member is not None


def can_delete_document(project, user=None):
    if user is None:
        user = current_user
    if not user.is_authenticated:
        return False

    # Lead Researcher (creator of the project)
    if project.creator_id == user.id:
        return True

    member = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=user.id,
    ).first()

    if not member:
        return False

    role = (member.role or "").strip().lower()
    return role in ["lead researcher", "creator", "co-researcher", "co researcher"]


@documents_bp.route("/projects/<int:project_id>/documents")
@login_required
def documents(project_id):
    project = Project.query.get_or_404(project_id)

    if not is_project_member(project):
        flash("Only project members can access documents.", "danger")
        return redirect(
            url_for(
                "projects.project_details",
                project_id=project_id,
            )
        )

    docs = Document.query.filter_by(
        project_id=project_id
    ).order_by(Document.upload_date.desc()).all()

    can_delete = can_delete_document(project)

    return render_template(
        "documents/documents.html",
        project=project,
        documents=docs,
        can_delete=can_delete,
    )


@documents_bp.route(
    "/projects/<int:project_id>/documents/upload",
    methods=["GET", "POST"],
)
@login_required
def upload_document(project_id):
    project = Project.query.get_or_404(project_id)

    if not is_project_member(project):
        flash("Only project members can upload documents.", "danger")
        return redirect(
            url_for(
                "projects.project_details",
                project_id=project_id,
            )
        )

    form = DocumentUploadForm()

    if form.validate_on_submit():
        uploaded_file = form.file.data
        original_filename = secure_filename(uploaded_file.filename)

        if not original_filename:
            flash("Invalid filename.", "danger")
            return redirect(
                url_for(
                    "documents.upload_document",
                    project_id=project_id,
                )
            )

        extension = original_filename.rsplit(".", 1)[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            flash("This file type is not allowed.", "danger")
            return redirect(
                url_for(
                    "documents.upload_document",
                    project_id=project_id,
                )
            )

        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)

        uploaded_file.save(file_path)

        # Initialize document instance
        document = Document(
            project_id=project.id,
            uploaded_by=current_user.id,
            filename=original_filename,
            file_path=file_path,
            file_type=uploaded_file.mimetype or extension,
        )

        # Automated PDF Metadata Extraction using PyMuPDF (fitz)
        if extension == "pdf":
            try:
                extracted = extract_pdf_metadata(file_path)
                document.paper_title = extracted.get("paper_title") or original_filename
                document.paper_authors = extracted.get("paper_authors")
                document.paper_abstract = extracted.get("paper_abstract")
                document.paper_keywords = extracted.get("paper_keywords")
                document.paper_conclusions = extracted.get("paper_conclusions")
                document.paper_gaps = extracted.get("paper_gaps")
                document.page_count = extracted.get("page_count", 1)
                document.creation_date = extracted.get("creation_date", "N/A")
                document.metadata_extracted = extracted.get("metadata_extracted", False)
                flash_msg = "Research paper uploaded"
            except Exception as e:
                document.metadata_extracted = False
                flash_msg = f"Document uploaded, but metadata extraction encountered an issue: {str(e)}"
        else:
            document.metadata_extracted = False
            flash_msg = "Document uploaded successfully."

        db.session.add(document)
        db.session.commit()

        flash(flash_msg, "success")
        return redirect(
            url_for(
                "documents.documents",
                project_id=project_id,
            )
        )

    return render_template(
        "documents/upload_document.html",
        project=project,
        form=form,
    )


@documents_bp.route("/documents/<int:document_id>")
@documents_bp.route("/documents/<int:document_id>/details")
@login_required
def document_details(document_id):
    document = Document.query.get_or_404(document_id)
    project = Project.query.get_or_404(document.project_id)

    if not is_project_member(project):
        flash("Only project members can view document details.", "danger")
        return redirect(
            url_for(
                "projects.project_details",
                project_id=project.id,
            )
        )

    can_delete = can_delete_document(project)

    return render_template(
        "documents/document_details.html",
        project=project,
        document=document,
        can_delete=can_delete,
    )


@documents_bp.route("/documents/<int:document_id>/reextract", methods=["POST"])
@login_required
def reextract_metadata(document_id):
    document = Document.query.get_or_404(document_id)
    project = Project.query.get_or_404(document.project_id)

    if not is_project_member(project):
        flash("Only project members can re-extract document metadata.", "danger")
        return redirect(url_for("projects.project_details", project_id=project.id))

    if not document.is_pdf:
        flash("Metadata extraction is only supported for PDF research papers.", "warning")
        return redirect(url_for("documents.document_details", document_id=document.id))

    if not os.path.exists(document.file_path):
        flash("Physical document file could not be found on server storage.", "danger")
        return redirect(url_for("documents.document_details", document_id=document.id))

    try:
        extracted = extract_pdf_metadata(document.file_path)
        document.paper_title = extracted.get("paper_title") or document.filename
        document.paper_authors = extracted.get("paper_authors")
        document.paper_abstract = extracted.get("paper_abstract")
        document.paper_keywords = extracted.get("paper_keywords")
        document.paper_conclusions = extracted.get("paper_conclusions")
        document.paper_gaps = extracted.get("paper_gaps")
        document.page_count = extracted.get("page_count", 1)
        document.creation_date = extracted.get("creation_date", "N/A")
        document.metadata_extracted = extracted.get("metadata_extracted", False)
        db.session.commit()
        flash("PDF metadata re-extracted successfully!", "success")
    except Exception as e:
        flash(f"Re-extraction failed: {str(e)}", "danger")

    return redirect(url_for("documents.document_details", document_id=document.id))


@documents_bp.route("/documents/<int:document_id>/download")
@login_required
def download_document(document_id):
    document = Document.query.get_or_404(document_id)
    project = Project.query.get_or_404(document.project_id)

    if not is_project_member(project):
        flash("Only project members can download documents.", "danger")
        return redirect(
            url_for(
                "projects.project_details",
                project_id=project.id,
            )
        )

    if not os.path.exists(document.file_path):
        flash("File not found on server.", "danger")
        return redirect(
            url_for(
                "documents.documents",
                project_id=project.id,
            )
        )

    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.filename,
    )


@documents_bp.route(
    "/documents/<int:document_id>/delete",
    methods=["POST"],
)
@login_required
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    project = Project.query.get_or_404(document.project_id)

    if not can_delete_document(project):
        flash("Only the Lead Researcher and Co-Researcher can delete documents.", "danger")
        return redirect(
            url_for(
                "documents.documents",
                project_id=project.id,
            )
        )

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.session.delete(document)
    db.session.commit()

    flash("Document deleted successfully.", "success")

    return redirect(
        url_for(
            "documents.documents",
            project_id=project.id,
        )
    )
