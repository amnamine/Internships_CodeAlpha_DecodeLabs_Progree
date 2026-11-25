import os
from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from models import db, User

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-project-management-tool')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_manager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    socketio.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.index'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Register HTTP routes blueprint
        from routes import main_bp
        app.register_blueprint(main_bp)

        # Import sockets to bind event handlers
        import sockets

        # Create database tables if they do not exist
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
