from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy.sql.expression import func

from website.documents.models import Document
from website.projects.models import JoinRequest, Project, ProjectMember, Task
from website.utils.decorators import check_is_confirmed

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
@login_required
@check_is_confirmed
def home():
    # 1. Projects created by the user and projects where the user is a member
    created_projects = (
        Project.query.filter_by(creator_id=current_user.id)
        .order_by(Project.created_on.desc())
        .all()
    )

    member_projects = (
        Project.query.join(
            ProjectMember, Project.id == ProjectMember.project_id
        )
        .filter(
            ProjectMember.user_id == current_user.id,
            Project.creator_id != current_user.id,
        )
        .order_by(Project.created_on.desc())
        .all()
    )

    all_user_projects = created_projects + member_projects
    all_project_ids = [p.id for p in all_user_projects]

    # 2. Aggregated Tasks across all user's projects
    if all_project_ids:
        all_tasks = (
            Task.query.filter(Task.project_id.in_(all_project_ids))
            .order_by(Task.created_on.desc())
            .all()
        )
    else:
        all_tasks = []

    pending_tasks = [
        t for t in all_tasks if t.status in ["Pending", "To Do", "Created"]
    ]
    in_progress_tasks = [
        t
        for t in all_tasks
        if t.status in ["InProgress", "In Progress", "Assigned"]
    ]
    completed_tasks = [
        t for t in all_tasks if t.status in ["Completed", "Done"]
    ]
    overdue_tasks = [
        t for t in all_tasks if t.status in ["Overdue", "overdue"]
    ]

    # 3. Recent Research Documents across user's projects
    if all_project_ids:
        recent_documents = (
            Document.query.filter(Document.project_id.in_(all_project_ids))
            .order_by(Document.upload_date.desc())
            .limit(6)
            .all()
        )
        total_docs_count = Document.query.filter(
            Document.project_id.in_(all_project_ids)
        ).count()
    else:
        recent_documents = []
        total_docs_count = 0

    # 4. Pending Collaboration Requests for projects created by user
    pending_requests_count = (
        JoinRequest.query.join(Project)
        .filter(
            Project.creator_id == current_user.id,
            JoinRequest.status == "pending",
        )
        .count()
    )

    # 5. Featured / Open Public Research Projects to discover
    public_query = Project.query.filter(Project.visibility == "public")
    if all_project_ids:
        public_query = public_query.filter(~Project.id.in_(all_project_ids))
    featured_projects = public_query.order_by(func.random()).limit(3).all()

    # 6. Summary metrics
    stats = {
        "total_projects": len(all_user_projects),
        "created_projects_count": len(created_projects),
        "member_projects_count": len(member_projects),
        "pending_tasks_count": len(pending_tasks),
        "in_progress_tasks_count": len(in_progress_tasks),
        "completed_tasks_count": len(completed_tasks),
        "overdue_tasks_count": len(overdue_tasks),
        "total_tasks_count": len(all_tasks),
        "total_documents_count": total_docs_count,
        "pending_requests_count": pending_requests_count,
    }

    return render_template(
        "core/index.html",
        stats=stats,
        created_projects=created_projects,
        member_projects=member_projects,
        all_user_projects=all_user_projects,
        pending_tasks=pending_tasks[:6],
        in_progress_tasks=in_progress_tasks[:6],
        completed_tasks=completed_tasks[:6],
        all_tasks=all_tasks[:8],
        recent_documents=recent_documents,
        featured_projects=featured_projects,
    )
