from flask import Flask
from config import Config
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    
    # Ensure upload directory exists
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    # Import models and routes
    from app.models import User, Document, Conversation, Message
    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.api import api
    
    # Set up login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add no-cache headers for static files to prevent caching issues
    @app.after_request
    def add_no_cache_headers(response):
        # Add no-cache headers for HTML pages and JavaScript files
        if (response.content_type and 
            ('text/html' in response.content_type or 
             'application/javascript' in response.content_type or
             'text/javascript' in response.content_type)):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(api, url_prefix='/api')
    
    return app