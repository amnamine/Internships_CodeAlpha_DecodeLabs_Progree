from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_project')
def on_join(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        join_room(room)
        print(f"Client {request.sid} joined room: {room}")

@socketio.on('leave_project')
def on_leave(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        leave_room(room)
        print(f"Client {request.sid} left room: {room}")

@socketio.on('task_moved')
def on_task_moved(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        # Broadcast the move to all other clients in the project room
        emit('task_moved_sync', data, to=room, include_self=False)

@socketio.on('task_created')
def on_task_created(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        emit('task_created_sync', data, to=room, include_self=False)

@socketio.on('task_updated')
def on_task_updated(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        emit('task_updated_sync', data, to=room, include_self=False)

@socketio.on('task_deleted')
def on_task_deleted(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        emit('task_deleted_sync', data, to=room, include_self=False)

@socketio.on('comment_added')
def on_comment_added(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        emit('comment_added_sync', data, to=room, include_self=False)

@socketio.on('member_added')
def on_member_added(data):
    project_id = data.get('project_id')
    if project_id:
        room = f"project_{project_id}"
        emit('member_added_sync', data, to=room, include_self=False)
