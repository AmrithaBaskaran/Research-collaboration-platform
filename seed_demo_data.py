import os
import fitz
from datetime import datetime
from website import app, db
from website.accounts.models import User, Profile
from website.projects.models import Project, ProjectMember, Task, Comment, JoinRequest
from website.documents.models import Document
from website.documents.extractor import extract_pdf_metadata

with app.app_context():
    # Clean existing data if any
    db.drop_all()
    db.create_all()
    print("Database reset and tables created.")

    # 1. Create Users
    u1 = User(email="mokshita@vit.ac.in", password="password123", is_confirmed=True, confirmed_on=datetime.now())
    u2 = User(email="amritha@vit.ac.in", password="password123", is_confirmed=True, confirmed_on=datetime.now())
    u3 = User(email="smrithi@vit.ac.in", password="password123", is_confirmed=True, confirmed_on=datetime.now())

    db.session.add_all([u1, u2, u3])
    db.session.commit()

    p1_profile = Profile(user_id=u1.id, full_name="Mokshita CV", age=20, bio="Lead Researcher at VIT Chennai", photo=None)
    p2_profile = Profile(user_id=u2.id, full_name="Amritha DB", age=20, bio="Co-Researcher & NLP Specialist", photo=None)
    p3_profile = Profile(user_id=u3.id, full_name="Smrithi S", age=20, bio="Faculty Guide & Research Supervisor", photo=None)
    db.session.add_all([p1_profile, p2_profile, p3_profile])
    db.session.commit()
    print("Users and Profiles created.")

    # 2. Create Projects
    proj1 = Project(
        name="Autonomous Research Collaboration & Multi-Agent Coordination",
        description="An end-to-end framework enabling student and faculty research teams to coordinate literature reviews, experiment workflows, and paper publishing.",
        creator_id=u1.id,
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

    # 3. Add Memberships
    m1 = ProjectMember(user_id=u1.id, project_id=proj1.id, role="Lead Researcher")
    m2 = ProjectMember(user_id=u2.id, project_id=proj1.id, role="Co-Researcher")
    m3 = ProjectMember(user_id=u3.id, project_id=proj1.id, role="Faculty Guide")

    m4 = ProjectMember(user_id=u3.id, project_id=proj2.id, role="Lead Researcher")
    m5 = ProjectMember(user_id=u1.id, project_id=proj2.id, role="Co-Researcher")

    db.session.add_all([m1, m2, m3, m4, m5])
    db.session.commit()
    print("Projects and Members created.")

    # 4. Create Tasks
    t1 = Task(
        name="Literature Review on Multi-Agent Academic Workflows",
        description="Survey 30 top-tier IEEE/ACM publications on distributed team collaboration tools and sociotechnical workflows.",
        status="Completed",
        role="Literature Review",
        project_id=proj1.id
    )
    t2 = Task(
        name="PyMuPDF Intelligent Metadata Extraction Engine",
        description="Implement regex section parsers and PDF property scrapers for automated title, abstract, keywords, and gap extraction.",
        status="Completed",
        role="Lead Researcher",
        project_id=proj1.id
    )
    t3 = Task(
        name="Multi-Agent Consensus Experimentation",
        description="Run benchmark experiments comparing context retention rates under heavy literature synthesis workloads.",
        status="InProgress",
        role="Methodology & Experiments",
        project_id=proj1.id
    )
    t4 = Task(
        name="Final Paper Manuscript Draft & Formatting",
        description="Draft methodology section and compile IEEE two-column camera-ready conference paper submission.",
        status="Pending",
        role="Paper Writing & Publication",
        project_id=proj1.id
    )
    t5 = Task(
        name="Memory Tree Benchmarking & Prior Formulation",
        description="Evaluate latency tradeoffs of buffered vs speculative context window allocation.",
        status="InProgress",
        role="Co-Researcher",
        project_id=proj2.id
    )

    db.session.add_all([t1, t2, t3, t4, t5])
    db.session.commit()

    # Add comments
    c1 = Comment(text="Initial literature survey completed! Found 28 relevant papers.", user_id=u2.id, task_id=t1.id)
    c2 = Comment(text="Great work, proceed with the extraction pipeline integration.", user_id=u1.id, task_id=t1.id)
    db.session.add_all([c1, c2])
    db.session.commit()
    print("Tasks and Comments created.")

    # 5. Create Sample Academic Research Paper PDF and Upload
    upload_dir = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    pdf_filename = "autonomous_research_collaboration_survey.pdf"
    unique_name = f"demo_{pdf_filename}"
    file_path = os.path.join(upload_dir, unique_name)

    doc = fitz.open()
    page = doc.new_page()
    paper_text = """Autonomous Multi-Agent Coordination for Academic Research Management
Dr. Mokshita CV, Amritha DB, Prof. Smrithi S
School of Computer Science and Engineering, VIT Chennai

Abstract
In this paper, we propose an intelligent web-based research collaboration platform designed to eliminate workflow fragmentation in academic research teams. By combining role-based milestone coordination with automated PyMuPDF research paper metadata extraction, our system reduces literature review synthesis overhead by 62%.

Keywords: Academic Collaboration, Literature Review, PyMuPDF, Metadata Extraction, Research Lifecycle

1. Introduction
Modern university research teams face severe communication fragmentation across disconnected chat apps, file drives, and task trackers...

2. Limitations and Research Gaps
Existing single-server systems fail to preserve PDF metadata across multiple collaborative sessions and lack contextual task-discussion integration.

3. Conclusions and Future Work
We demonstrated an end-to-end framework for academic project tracking and intelligent literature indexing. Future work includes expanding the extraction pipeline to support multi-modal chart and table analysis.

References
[1] Vaswani et al., Attention is All You Need, 2017.
[2] Dean and Ghemawat, MapReduce: Simplified Data Processing, 2004.
"""
    page.insert_text((50, 50), paper_text)
    doc.set_metadata({
        "title": "Autonomous Multi-Agent Coordination for Academic Research Management",
        "author": "Dr. Mokshita CV, Amritha DB, Prof. Smrithi S",
        "keywords": "Academic Collaboration, Literature Review, PyMuPDF, Metadata Extraction",
    })
    doc.save(file_path)
    doc.close()

    # Extract metadata using our extractor
    extracted = extract_pdf_metadata(file_path)

    doc_entry = Document(
        project_id=proj1.id,
        uploaded_by=u1.id,
        filename=pdf_filename,
        file_path=file_path,
        file_type="application/pdf",
        paper_title=extracted["paper_title"],
        paper_authors=extracted["paper_authors"],
        paper_abstract=extracted["paper_abstract"],
        paper_keywords=extracted["paper_keywords"],
        paper_conclusions=extracted["paper_conclusions"],
        paper_gaps=extracted["paper_gaps"],
        page_count=extracted["page_count"],
        creation_date=extracted["creation_date"],
        metadata_extracted=True,
    )
    db.session.add(doc_entry)
    db.session.commit()
    print("Sample research PDF generated and indexed with PyMuPDF.")

    print("\n✅ SEEDING COMPLETE! Login credentials:")
    print("   Lead Researcher: mokshita@vit.ac.in / password123")
    print("   Co-Researcher:   amritha@vit.ac.in  / password123")
    print("   Faculty Guide:   smrithi@vit.ac.in  / password123")
