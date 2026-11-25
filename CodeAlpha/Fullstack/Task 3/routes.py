import random
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Project, ProjectMember, Task, Comment, Notification

main_bp = Blueprint('main', __name__)

AVATAR_COLORS = [
    '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', 
    '#10b981', '#14b8a6', '#0ea5e9', '#f59e0b'
]

# Dashboard route
@main_bp.route('/')
def index():
    return render_template('index.html')

# Authentication APIs
@main_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(
        username=username,
        email=email,
        avatar_color=random.choice(AVATAR_COLORS)
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=True)
    return jsonify({'message': 'Registration successful', 'user': new_user.to_dict()}), 201

@main_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    login_user(user, remember=True)
    return jsonify({'message': 'Login successful', 'user': user.to_dict()})

@main_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@main_bp.route('/api/auth/me', methods=['GET'])
def get_me():
    if current_user.is_authenticated:
        return jsonify({'user': current_user.to_dict()})
    return jsonify({'user': None})

# Users API
@main_bp.route('/api/users', methods=['GET'])
@login_required
def list_users():
    users = User.query.filter(User.id != current_user.id).all()
    return jsonify([u.to_dict() for u in users])

# Projects API
@main_bp.route('/api/projects', methods=['GET'])
@login_required
def list_projects():
    # Fetch projects where user is owner or member
    projects = current_user.projects.all()
    # Also fetch owned projects just in case
    owned = current_user.owned_projects
    all_projects = list(set(projects + owned))
    return jsonify([p.to_dict() for p in all_projects])

@main_bp.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return jsonify({'error': 'Project name is required'}), 400

    new_project = Project(
        name=name,
        description=description,
        owner_id=current_user.id
    )
    db.session.add(new_project)
    db.session.commit()

    # Add owner as member automatically
    member = ProjectMember(project_id=new_project.id, user_id=current_user.id, role='Owner')
    db.session.add(member)
    db.session.commit()

    return jsonify(new_project.to_dict()), 201

@main_bp.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check membership
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    # Fetch members details
    members = []
    project_members = ProjectMember.query.filter_by(project_id=project.id).all()
    for pm in project_members:
        u = User.query.get(pm.user_id)
        if u:
            user_data = u.to_dict()
            user_data['role'] = pm.role
            members.append(user_data)

    # Fetch tasks
    tasks = [t.to_dict() for t in project.tasks]

    project_data = project.to_dict()
    project_data['members'] = members
    project_data['tasks'] = tasks

    return jsonify(project_data)

@main_bp.route('/api/projects/<int:project_id>/invite', methods=['POST'])
@login_required
def invite_member(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check permissions (only Owner can invite or any member, let's allow all members for collaboration, or only owner. Let's do all members to keep it collaborative)
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    data = request.get_json() or {}
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    target_user = User.query.filter_by(username=username).first()
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    existing_member = ProjectMember.query.filter_by(project_id=project.id, user_id=target_user.id).first()
    if existing_member:
        return jsonify({'error': 'User is already a member of this project'}), 400

    new_member = ProjectMember(project_id=project.id, user_id=target_user.id, role='Member')
    db.session.add(new_member)

    # Create notification for target user
    noti = Notification(
        user_id=target_user.id,
        message=f"{current_user.username} added you to the project '{project.name}'."
    )
    db.session.add(noti)
    db.session.commit()

    return jsonify({'message': 'Member invited successfully', 'user': target_user.to_dict()})

# Tasks API
@main_bp.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    status = data.get('status', 'Todo')
    priority = data.get('priority', 'Medium')
    due_date = data.get('due_date', None)
    assignee_id = data.get('assignee_id', None)

    if not title:
        return jsonify({'error': 'Task title is required'}), 400

    new_task = Task(
        project_id=project.id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        assignee_id=assignee_id,
        creator_id=current_user.id
    )

    db.session.add(new_task)
    db.session.commit()

    # Trigger notification if task is assigned to someone else
    if assignee_id and assignee_id != current_user.id:
        noti = Notification(
            user_id=assignee_id,
            message=f"{current_user.username} assigned you the task '{title}' in project '{project.name}'."
        )
        db.session.add(noti)
        db.session.commit()

    return jsonify(new_task.to_dict()), 201

@main_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    data = request.get_json() or {}
    
    # Check who was the old assignee to notify if assignee changes
    old_assignee_id = task.assignee_id

    if 'title' in data:
        task.title = data['title'].strip() or task.title
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = data['due_date']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']

    db.session.commit()

    # If assignee changed, notify the new assignee
    if task.assignee_id and task.assignee_id != old_assignee_id and task.assignee_id != current_user.id:
        noti = Notification(
            user_id=task.assignee_id,
            message=f"{current_user.username} assigned you the task '{task.title}' in project '{project.name}'."
        )
        db.session.add(noti)
        db.session.commit()

    return jsonify(task.to_dict())

@main_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully', 'id': task_id})

# Comments API
@main_bp.route('/api/tasks/<int:task_id>/comments', methods=['GET'])
@login_required
def get_comments(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    comments = [c.to_dict() for c in task.comments]
    return jsonify(comments)

@main_bp.route('/api/tasks/<int:task_id>/comments', methods=['POST'])
@login_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    
    is_member = ProjectMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if not is_member:
        abort(403)

    data = request.get_json() or {}
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'error': 'Comment content cannot be empty'}), 400

    new_comment = Comment(
        task_id=task.id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(new_comment)
    db.session.commit()

    # Notify assignee if someone else comments on their task
    if task.assignee_id and task.assignee_id != current_user.id:
        noti = Notification(
            user_id=task.assignee_id,
            message=f"{current_user.username} commented on your task '{task.title}': \"{content[:30]}...\""
        )
        db.session.add(noti)
        db.session.commit()

    return jsonify(new_comment.to_dict()), 201

# Notifications API
@main_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications])

@main_bp.route('/api/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    db.session.query(Notification).filter_by(user_id=current_user.id).update({Notification.is_read: True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'})
