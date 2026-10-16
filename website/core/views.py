from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy.sql.expression import func

from website.documents.models import Document
from website.projects.models import JoinRequest, Project, ProjectMember, Task
from website.utils.decorators import check_is_confirmed

from datetime import datetime
from website import db
from website.accounts.models import User, Profile
from website.projects.models import Comment

core_bp = Blueprint("core", __name__)


def ensure_seed_data(user=None):
    try:
        if Project.query.count() == 0:
            u1 = User.query.filter_by(email="mokshita@vit.ac.in").first()
            if not u1:
                u1 = User(email="mokshita@vit.ac.in", password="password123", is_confirmed=True, confirmed_on=datetime.now())
                db.session.add(u1)
                db.session.commit()
                p1 = Profile(user_id=u1.id, full_name="Mokshita CV", age=20, bio="Lead Researcher at VIT Chennai", photo=None)
                db.session.add(p1)

            u2 = User.query.filter_by(email="amritha@vit.ac.in").first()
            if not u2:
                u2 = User(email="amritha@vit.ac.in", password="password123", is_confirmed=True, confirmed_on=datetime.now())
                db.session.add(u2)
                db.session.commit()
                p2 = Profile(user_id=u2.id, full_name="Amritha DB", age=20, bio="Co-Researcher & NLP Specialist", photo=None)
                db.session.add(p2)

            u3 = User.query.filter_by(email="smrithi@vit.ac.in").first()
            if not u3:
                u3 = User(email="smrithi@vit.ac.in", password="password123", is_confirmed=True, confirmed_on=datetime.now())
                db.session.add(u3)
                db.session.commit()
                p3 = Profile(user_id=u3.id, full_name="Smrithi S", age=20, bio="Faculty Guide & Research Supervisor", photo=None)
                db.session.add(p3)

            db.session.commit()

            creator_id = user.id if user and user.is_authenticated else u1.id
            proj1 = Project(
                name="Autonomous Research Collaboration & Multi-Agent Coordination",
                description="An end-to-end framework enabling student and faculty research teams to coordinate literature reviews, experiment workflows, and paper publishing.",
                creator_id=creator_id,
                visibility="public"
            )
            proj2 = Project(
                name="Distributed Neural Memory Indexing for Infinite LLM Reasoning",
                description="Investigating hierarchical memory tree indexing to overcome context rot and degradation in long-horizon coding and scientific reasoning.",
                creator_id=u3.id,
                visibility="public"
            )
            proj3 = Project(
                name="Zero-Knowledge Verification for Academic Peer Review",
                description="Exploring privacy-preserving cryptographic protocols for double-blind academic reviews and citation credibility.",
                creator_id=u2.id,
                visibility="public"
            )
            db.session.add_all([proj1, proj2, proj3])
            db.session.commit()

            m1 = ProjectMember(user_id=u1.id, project_id=proj1.id, role="Lead Researcher")
            m2 = ProjectMember(user_id=u2.id, project_id=proj1.id, role="Co-Researcher")
            m3 = ProjectMember(user_id=u3.id, project_id=proj1.id, role="Faculty Guide")
            m4 = ProjectMember(user_id=u3.id, project_id=proj2.id, role="Lead Researcher")
            m5 = ProjectMember(user_id=u1.id, project_id=proj2.id, role="Co-Researcher")
            db.session.add_all([m1, m2, m3, m4, m5])

            t1 = Task(name="Literature Review on Multi-Agent Academic Workflows", description="Survey 30 top-tier IEEE/ACM publications on distributed team collaboration tools.", status="Completed", role="Literature Review", project_id=proj1.id)
            t2 = Task(name="PyMuPDF Intelligent Metadata Extraction Engine", description="Implement regex section parsers and PDF property scrapers.", status="Completed", role="Lead Researcher", project_id=proj1.id)
            t3 = Task(name="Multi-Agent Consensus Experimentation", description="Run benchmark experiments comparing context retention rates.", status="InProgress", role="Methodology & Experiments", project_id=proj1.id)
            t4 = Task(name="Final Paper Manuscript Draft & Formatting", description="Draft methodology section and compile IEEE two-column paper.", status="Pending", role="Paper Writing & Publication", project_id=proj1.id)
            t5 = Task(name="Memory Tree Benchmarking & Prior Formulation", description="Evaluate latency tradeoffs of buffered vs speculative context window allocation.", status="InProgress", role="Co-Researcher", project_id=proj2.id)
            db.session.add_all([t1, t2, t3, t4, t5])
            db.session.commit()

            c1 = Comment(text="Initial literature survey completed! Found 28 relevant papers.", user_id=u2.id, task_id=t1.id)
            c2 = Comment(text="Great work, proceed with the extraction pipeline integration.", user_id=u1.id, task_id=t1.id)
            db.session.add_all([c1, c2])
            db.session.commit()

            doc_entry = Document(
                project_id=proj1.id,
                uploaded_by=u1.id,
                filename="autonomous_research_collaboration_survey.pdf",
                file_path="uploads/demo_autonomous_research_collaboration_survey.pdf",
                file_type="application/pdf",
                paper_title="Autonomous Multi-Agent Coordination for Academic Research Management",
                paper_authors="Dr. Mokshita CV, Amritha DB, Prof. Smrithi S",
                paper_abstract="In this paper, we propose an intelligent web-based research collaboration platform designed to eliminate workflow fragmentation in academic research teams. By combining role-based milestone coordination with automated PyMuPDF research paper metadata extraction, our system reduces literature review synthesis overhead by 62%.",
                paper_keywords="Academic Collaboration, Literature Review, PyMuPDF, Metadata Extraction",
                paper_conclusions="We demonstrated an end-to-end framework for academic project tracking and intelligent literature indexing.",
                paper_gaps="Existing single-server systems fail to preserve PDF metadata across multiple collaborative sessions.",
                page_count=2,
                creation_date="2026",
                metadata_extracted=True,
            )
            db.session.add(doc_entry)
            db.session.commit()

        if user and user.is_authenticated:
            user_has_projects = Project.query.filter_by(creator_id=user.id).first() or ProjectMember.query.filter_by(user_id=user.id).first()
            if not user_has_projects:
                for p in Project.query.all():
                    if p.creator_id != user.id and not ProjectMember.query.filter_by(user_id=user.id, project_id=p.id).first():
                        db.session.add(ProjectMember(user_id=user.id, project_id=p.id, role="Researcher"))
                db.session.commit()
    except Exception as e:
        print(f"ensure_seed_data notice: {e}")
        db.session.rollback()


@core_bp.route("/")
@login_required
@check_is_confirmed
def home():
    ensure_seed_data(current_user)
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
