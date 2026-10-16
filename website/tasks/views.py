from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from website import app, db

from website.projects.models import Task, Project, ProjectMember
from website.tasks.forms import TaskForm

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)

    is_creator = current_user.id == project.creator_id
    is_member = (
        ProjectMember.query.filter_by(
            project_id=project.id, user_id=current_user.id
        ).first()
        is not None
    )

    if not is_creator and not is_member:
        flash("You do not have permission to edit this task.", "danger")
        return redirect(url_for("projects.project_details", project_id=task.project_id))

    form = TaskForm(obj=task)

    if form.validate_on_submit():
        form.populate_obj(task)
        db.session.commit()
        flash("Task updated successfully.", "success")
        return redirect(url_for("projects.project_details", project_id=task.project_id))

    return render_template(
        "tasks/edit_task.html",
        form=form,
        task=task,
        project=project,
        is_creator=is_creator,
    )


@tasks_bp.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    project = Project.query.get_or_404(project_id)

    is_creator = current_user.id == project.creator_id
    is_member = (
        ProjectMember.query.filter_by(
            project_id=project_id, user_id=current_user.id
        ).first()
        is not None
    )

    if not is_creator and not is_member:
        flash("You do not have permission to delete this task.", "danger")
        return redirect(url_for("projects.project_details", project_id=project_id))

    task_name = task.name
    db.session.delete(task)
    db.session.commit()
    flash(f"Task '{task_name}' deleted successfully.", "success")

    ref = request.referrer
    if ref and (f"/tasks/{task_id}" not in ref) and (f"/task/{task_id}" not in ref):
        return redirect(ref)
    return redirect(url_for("projects.project_details", project_id=project_id))
