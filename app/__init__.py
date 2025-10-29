from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
    app.config['SECRET_KEY'] = 'supersecretkey'  # change this in production!

    db.init_app(app)
    migrate.init_app(app, db)

    # 🔹 Initialize login manager *after* app is created
    login_manager.init_app(app)

    # 🔹 Import models after db initialized (to avoid circular imports)
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔹 Register blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
