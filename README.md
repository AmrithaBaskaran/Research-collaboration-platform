# 📚 Research Collaboration & Paper Management Platform
## Complete Codebase & Folder Architecture Documentation

---

## 👥 Project Information
- **Project Title:** Research Collaboration and Paper Management Platform
- **Base Architecture:** Adapted and extended from `flask-project-tracker`
- **Team Members:**
  - **Amritha DB** — `24BCE5064`
  - **Mokshita CV** — `24BCE1094`
  - **Smrithi S** — `24BCE1698`
- **Institution:** VIT Chennai
- **Target Submission:** Academic College Project Review & Evaluation

---

## 🧭 High-Level Project Directory Structure

```
flask-project-tracker/
├── main.py                     # Application entry point & custom CLI commands
├── config.py                   # Configuration settings for different environments
├── requirements.txt            # Python dependencies and libraries
├── PROJECT_REVIEW_GUIDE.md     # In-depth viva and presentation preparation guide
├── README.md                   # This file: Comprehensive codebase tour
├── Dockerfile                  # Container definition for Docker deployment
├── docker-compose.yml          # Multi-container orchestration (App + PostgreSQL)
├── setup.sh                    # Automated setup bash script
├── start.sh                    # Startup bash script
├── .env                        # Local environment variables and secrets
│
├── migrations/                 # Alembic database migration scripts (Schema history)
│   ├── alembic.ini             # Alembic configuration
│   ├── env.py                  # Migration execution environment
│   └── versions/               # Schema version migration scripts
│       ├── 1b1e50efdf29_initial_migration.py
│       ├── 62509f9810df_.py
│       └── 5c3dcd2dd586_add_documents_table.py
│
├── uploads/                    # Physical server storage for PDFs, avatars, and archives
│
├── tests/                      # Automated unit tests
│   ├── base_test.py            # Base test case setup with in-memory SQLite
│   ├── test_config.py          # Configuration tests
│   ├── test_forms.py           # Form validation tests
│   └── test_routes.py          # HTTP route response tests
│
└── website/                    # CORE APPLICATION PACKAGE (Flask Application)
    ├── __init__.py             # Flask App Factory & Extension Initializer
    │
    ├── accounts/               # MODULE 1: AUTHENTICATION & PROFILES
    │   ├── models.py           # User & Profile SQLAlchemy database models
    │   ├── forms.py            # WTForms for Login, Register, Profile edit
    │   ├── views.py            # Authentication routes & profile management logic
    │   └── token.py            # Cryptographic token generator for email links
    │
    ├── projects/               # MODULE 2: PROJECTS & COLLABORATION
    │   ├── models.py           # Project, ProjectMember, JoinRequest, Task, Comment models
    │   ├── forms.py            # WTForms for Project CRUD, Invites, Join Requests
    │   └── views.py            # Project CRUD, Member management, Task comments routes
    │
    ├── tasks/                  # MODULE 3: TASK MANAGEMENT
    │   ├── forms.py            # WTForms for Task creation, status updates
    │   └── views.py            # Task edit and delete route handlers
    │
    ├── documents/              # MODULE 4: DOCUMENT MANAGEMENT
    │   ├── models.py           # Document SQLAlchemy database model
    │   ├── forms.py            # WTForms for Document Upload with validation
    │   └── views.py            # Upload, List, Download, and Delete routes
    │
    ├── core/                   # MODULE 5: CORE & DASHBOARD
    │   └── views.py            # Home page and aggregated dashboard route
    │
    ├── utils/                  # UTILITIES & HELPERS
    │   ├── decorators.py       # Custom view access decorators (@logout_required, etc.)
    │   └── email.py            # Flask-Mail integration for outbound notifications
    │
    ├── static/                 # STATIC FRONTEND ASSETS
    │   └── styles/             # CSS stylesheets (base, projects, tasks, accounts)
    │
    └── templates/              # JINJA2 SERVER-RENDERED HTML TEMPLATES
        ├── _base.html          # Global layout template (Navbar, Flash alerts, Footer)
        ├── navigation.html     # Responsive Bootstrap navigation bar
        ├── accounts/           # Auth templates (login, register, profile, edit_profile)
        ├── projects/           # Project templates (projects, details, public, requests)
        ├── tasks/              # Task templates (details, edit, add_comment)
        ├── documents/          # Document templates (documents.html, upload_document.html)
        └── errors/             # Custom HTTP error pages (401, 404, 500)
```

---

# 📂 Detailed Breakdown of Every Folder & File

---

## 1. 根 Root Directory Files

### `main.py`
- **What it does:** The main executable script that starts the Flask development server and provides command-line interface (CLI) commands.
- **Key Code & Functions:**
  - `app.run()`: Starts the local web server at `http://127.0.0.1:5000`.
  - `@app.cli.command("create_admin")`: Command-line command (`flask create_admin`) allowing administrators to create superuser accounts interactively from the terminal.
  - `@app.cli.command("test")`: Runs automated unit tests located in the `tests/` directory and outputs results to `log_test.txt`.

### `config.py`
- **What it does:** Centralized environment configuration management. Loads secrets and paths from `.env`.
- **Key Classes:**
  - `Config`: Base configuration containing database connection strings (`SQLALCHEMY_DATABASE_URI`), encryption salts (`SECURITY_PASSWORD_SALT`), mail server settings, and upload destination (`UPLOAD_FOLDER = os.path.join(basedir, "uploads")`).
  - `DevelopmentConfig(Config)`: Enables `DEBUG = True` and debug toolbars for local work.
  - `TestingConfig(Config)`: Uses in-memory SQLite (`sqlite:///:memory:`) for running isolated unit tests.
  - `ProductionConfig(Config)`: Production-ready settings with debugging disabled.

### `requirements.txt`
- **What it does:** Lists the exact pinned versions of all Python packages required to run the project.
- **Key Libraries Included:**
  - `Flask==3.0.2`: Web framework.
  - `Flask-SQLAlchemy==3.1.1` & `psycopg2-binary==2.9.9`: PostgreSQL ORM.
  - `Flask-Login==0.6.3`: User session management.
  - `Flask-Bcrypt==1.0.1`: Password hashing.
  - `Flask-WTF==1.2.1` & `WTForms==3.1.2`: Forms & CSRF protection.
  - `Flask-Migrate==4.0.5` & `alembic==1.13.1`: Database migrations.
  - `pymupdf==1.26.5`: PDF parsing and metadata extraction engine.

### `PROJECT_REVIEW_GUIDE.md`
- **What it does:** An extensive college review defense guide containing architectural diagrams, technical justifications, 20+ viva questions & answers, and a live demonstration script for professors.

---

## 2. 🗃️ `website/` — Core Application Package

### `website/__init__.py` (The Application Factory)
- **What it does:** The heart of the Flask application. It initializes all third-party Flask extensions and binds them to the application instance.
- **Key Code & Logic:**
  - Initializes extensions: `db = SQLAlchemy(app)`, `bcrypt = Bcrypt(app)`, `login_manager = LoginManager(app)`, `csrf = CSRFProtect(app)`, `migrate = Migrate(app, db)`.
  - Registers Blueprints:
    - `app.register_blueprint(accounts_bp)`
    - `app.register_blueprint(projects_bp)`
    - `app.register_blueprint(tasks_bp)`
    - `app.register_blueprint(documents_bp)`
    - `app.register_blueprint(core_bp)`
  - `@login_manager.user_loader def load_user(user_id)`: Reloads user objects from the PostgreSQL database using the session ID stored in user cookies.
  - Custom HTTP error handlers for `401 Unauthorized`, `404 Page Not Found`, and `500 Server Error`.

---

## 3. 👤 `website/accounts/` — Authentication & Profile Module

Handles user registration, login, logout, password hashing, and user profile management.

### `website/accounts/models.py`
- **Classes:**
  - `class User(UserMixin, db.Model)`:
    - Database table: `users`
    - Fields: `id`, `email`, `password` (hashed with Bcrypt), `created_on`, `is_admin`, `is_confirmed`, `confirmed_on`.
    - Relationships: Has a 1-to-1 relationship with `Profile` (`cascade="all, delete-orphan"`).
    - Constructor automatically runs `bcrypt.generate_password_hash(password, rounds=10)`.
  - `class Profile(db.Model)`:
    - Database table: `profiles`
    - Fields: `id`, `user_id` (foreign key), `full_name`, `age`, `bio`, `photo`.

### `website/accounts/forms.py`
- **Classes:**
  - `LoginForm(FlaskForm)`: Fields for `email`, `password`, and `submit`.
  - `RegisterForm(FlaskForm)`: Validates email uniqueness and password confirmation.
  - `ProfileForm(FlaskForm)`: Fields for editing `full_name`, `age`, `bio`, and `profile_photo` (`FileField`).

### `website/accounts/views.py` (Blueprint: `accounts_bp`)
- **Key Routes & Logic:**
  - `GET/POST /register`: Registers new users. Creates the `User` and `Profile` records. Auto-confirms accounts for local development and logs the user in immediately.
  - `GET/POST /login`: Validates credentials with `bcrypt.check_password_hash` and calls `login_user()`.
  - `GET /logout`: Calls `logout_user()` and destroys the session.
  - `GET /profile`: Displays user details and profile picture.
  - `GET/POST /profile/edit`: Allows updating bio, age, name, and uploading new profile pictures to `uploads/`.
  - `POST /profile/delete_photo`: Resets profile picture back to `default_photo.jpg`.

### `website/accounts/token.py`
- **What it does:** Uses `itsdangerous.URLSafeTimedSerializer` to generate and verify cryptographically signed, timestamped tokens for email confirmation.

---

## 4. 🚀 `website/projects/` — Projects & Collaboration Module

Handles research project creation, team invitations, join requests, and task-level discussions.

### `website/projects/models.py`
- **Classes:**
  - `class Project(db.Model)`:
    - Database table: `projects`
    - Fields: `id`, `name`, `description`, `created_on`, `creator_id` (foreign key), `visibility` (`public` or `private`).
    - Relationships: Links to `tasks`, `members` (`ProjectMember`), `documents`, and `join_requests` with cascade delete.
  - `class ProjectMember(db.Model)`:
    - Database table: `project_members` (Join table for team collaboration).
    - Fields: `id`, `user_id` (foreign key), `project_id` (foreign key), `role` (*Lead Researcher*, *Member*, *Faculty Guide*).
  - `class JoinRequest(db.Model)`:
    - Database table: `join_requests`
    - Fields: `id`, `user_id`, `project_id`, `sender_id`, `sender_type`, `status` (*pending*, *accepted*, *rejected*), `role`, `message`.
  - `class Task(db.Model)`:
    - Database table: `tasks`
    - Fields: `id`, `name`, `description`, `created_on`, `status` (*Pending*, *InProgress*, *Completed*), `role`, `project_id` (foreign key).
    - Relationships: Links to `comments` with cascade delete.
  - `class Comment(db.Model)`:
    - Database table: `comments`
    - Fields: `id`, `text`, `created_on`, `user_id` (foreign key), `task_id` (foreign key).

### `website/projects/forms.py`
- **Classes:**
  - `CreateProjectForm`: Fields for project name, description, and visibility.
  - `EditProjectForm`: Edit existing project attributes.
  - `InviteMemberForm`: Allows project leads to invite users by typing their registered email and choosing a role.
  - `SendJoinRequestForm`: Form for applicants to apply to join public projects.
  - `AcceptRequestForm` / `RejectRequestForm`: For project leads to approve or decline applicants.

### `website/projects/views.py` (Blueprint: `projects_bp`)
- **Key Routes & Logic:**
  - `GET /projects`: Shows "Created Projects" and "Member Projects".
  - `GET/POST /projects/create`: Creates a new project and assigns the creator as team lead in `project_members`.
  - `GET /projects/<id>`: Project Hub showing project details, members, tasks, and the **Documents** button.
  - `GET/POST /projects/<id>/send_request`: Submits a collaboration request.
  - `POST /accept_request/<id>` & `/reject_request/<id>`: Processes incoming join requests.
  - `POST /projects/<id>/invite`: Directly adds a member by email.
  - `POST /projects/<id>/remove_member/<member_id>`: Removes a collaborator.
  - `GET /projects/<id>/tasks/<task_id>`: Opens task details and displays threaded comments.
  - `POST /projects/<id>/tasks/<task_id>/add_comment`: Adds a comment to a task.
  - `POST /comments/<id>/delete`: Deletes a comment if the user is author or project creator.

---

## 5. ✅ `website/tasks/` — Task Management Module

### `website/tasks/forms.py`
- `TaskForm`: Fields for task `name`, `description`, `status` (*Pending*, *InProgress*, *Completed*), and target `role`.
- `CommentForm`: Textarea for adding comments to tasks.

### `website/tasks/views.py` (Blueprint: `tasks_bp`)
- `GET/POST /task/<id>/edit`: Edits task name, description, or status.
- `POST /task/<id>/delete`: Deletes a task and all associated comments.

---

## 6. 📄 `website/documents/` — Document Management Module

**Our team's original contribution.** Enables uploading, viewing, downloading, and deleting project-scoped research documents and PDFs.

### `website/documents/models.py`
- **Classes:**
  - `class Document(db.Model)`:
    - Database table: `documents`
    - Fields:
      - `id` (Integer, Primary Key)
      - `project_id` (Foreign Key $\rightarrow$ `projects.id`)
      - `uploaded_by` (Foreign Key $\rightarrow$ `users.id`)
      - `filename` (String 255): Original sanitized filename
      - `file_path` (String 500): Absolute disk storage path in `uploads/`
      - `file_type` (String 100): MIME type / extension (`application/pdf`, etc.)
      - `upload_date` (DateTime): Upload timestamp

### `website/documents/forms.py`
- **Classes:**
  - `DocumentUploadForm(FlaskForm)`:
    - `file = FileField("Document", validators=[FileRequired(), FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'zip'])])`
    - `submit = SubmitField("Upload Document")`

### `website/documents/views.py` (Blueprint: `documents_bp`)
- **Key Functions & Routes:**
  - `is_project_member(project)`: Security helper that verifies if `current_user` is the creator or listed in `project_members`.
  - `GET /projects/<id>/documents`: Lists all uploaded documents for that project.
  - `GET/POST /projects/<id>/documents/upload`:
    1. Validates user membership.
    2. Runs `secure_filename()` on uploaded file.
    3. Prepends unique `uuid.uuid4().hex` to prevent filename collisions.
    4. Saves file to `current_app.config["UPLOAD_FOLDER"]`.
    5. Saves `Document` record in PostgreSQL.
  - `GET /documents/<id>/download`: Securely streams file to client using `flask.send_file(as_attachment=True)`.
  - `POST /documents/<id>/delete`: Deletes file from disk and deletes database record.

---

## 7. 🏠 `website/core/` — Core & Dashboard Module

### `website/core/views.py` (Blueprint: `core_bp`)
- **Routes:**
  - `GET /`: Protected landing page showing personalized welcome, platform updates, and public featured projects.

---

## 8. 🛠️ `website/utils/` — Decorators & Helper Utilities

### `website/utils/decorators.py`
- `@logout_required`: Redirects already logged-in users away from `/login` or `/register` to the home page.
- `@check_is_confirmed`: Ensures users have active accounts before accessing features.

### `website/utils/email.py`
- `send_email(to, subject, template)`: Asynchronously formats and sends HTML emails via `Flask-Mail`.

---

## 9. 🎨 `website/templates/` — Jinja2 HTML UI Templates

- **`_base.html`**: Master template loaded by all pages. Imports Bootstrap 5 CSS/JS, renders flash messages (`flash()`), and includes `navigation.html`.
- **`navigation.html`**: Top navigation bar that conditionally displays links for Home, Your Projects, Open Projects, Requests, Profile, and Login/Logout buttons based on `current_user.is_authenticated`.
- **`accounts/`**:
  - `login.html`: Email and password login form.
  - `register.html`: New user registration form.
  - `profile.html` & `edit_profile.html`: View and update user profile data and avatar.
- **`projects/`**:
  - `projects.html`: Split view showing "Created Projects" vs "Member Projects".
  - `create_project.html`: Project creation form.
  - `project_details.html`: Comprehensive Project Hub with member list, add task, edit project, and the **Documents** button.
  - `public_projects.html`: Search and browse open research projects.
  - `projects_requests.html`: Lead Researcher review panel for accepting/rejecting join requests.
- **`tasks/`**:
  - `task_details.html`: Displays task status, assignee, and the live threaded comment feed.
  - `add_comment_to_task.html` & `edit_task.html`: Forms for updating tasks and posting comments.
- **`documents/`**:
  - `documents.html`: Document Library table showing filename, type, uploader, upload timestamp, Download button, and Delete button.
  - `upload_document.html`: File picker form with allowed extension badges.
- **`errors/`**: Custom, user-friendly error templates for HTTP `401`, `404`, and `500`.

---

## 10. 🗄️ `migrations/` — Database Schema Versioning

- **`migrations/versions/5c3dcd2dd586_add_documents_table.py`**:
  - Contains Alembic migration code that automatically created the `documents` table in PostgreSQL with all foreign keys linked to `projects.id` and `users.id`.

---

## 11. 📂 `uploads/` — Local Server Storage

- **What it is:** The physical directory on the server disk where uploaded profile photos and research documents (PDFs, images, ZIPs) are saved.
- **Naming format:** Files are stored with secure UUID prefixes (e.g. `c4d8e2f10b7a_paper.pdf`) so that two users uploading a file named `paper.pdf` will never overwrite each other.

---

## 12. 🧪 `tests/` — Automated Unit Testing

- `base_test.py`: Sets up a lightweight in-memory SQLite database (`sqlite:///:memory:`) before each test and tears it down after.
- `test_config.py`: Verifies development, testing, and production configuration parameters.
- `test_forms.py`: Tests that WTForms correctly catch invalid email formats, missing passwords, and disallowed file types.
- `test_routes.py`: Tests that protected routes return HTTP 302 redirects to login for unauthorized users.

---

# 🎯 Summary for Professors & Evaluators
This project structure follows industry-standard **Flask Blueprint modularity**, adheres to **MVC separation of concerns**, protects data using **Bcrypt salted hashing** and **CSRF tokens**, and provides a dedicated, secure **Document Management System** ready for PyMuPDF-based research paper metadata extraction.
